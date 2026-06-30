/**
 * app.cpp — Macro HTTP Server (C++ backend)
 *
 * Replaces app.py (Flask). Serves the same API surface:
 *   GET /                           → dashboard.html
 *   GET /name                       → server name (plain text)
 *   GET /api/config                 → JSON config
 *   GET /api/library/<type>         → JSON array from SQLite
 *   GET /api/stream/<type>/<id>     → byte-range capable media streaming
 *   GET /api/search/<type>?q=...    → JSON search results
 *   GET /<client>/                  → client/home.html
 *   GET /<client>/<path>            → static file under clients/
 *
 * Build: bazel build //server:macro_server
 * Run:   ./bazel-bin/server/macro_server [port]
 */

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

#include "httplib.h"

#include <SQLiteCpp/SQLiteCpp.h>
#include <sqlite3.h>          // for SQLITE_INTEGER / SQLITE_FLOAT / SQLITE_NULL
#include <nlohmann/json.hpp>

namespace fs = std::filesystem;
using json = nlohmann::json;

// ── Helpers ──────────────────────────────────────────────────────────────────

static std::string g_base_dir;   // directory of the binary (server/)
static std::string g_clients_dir; // server/clients/

// Read a whole file as string. Returns "" on failure.
static std::string read_file(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) return "";
    return {std::istreambuf_iterator<char>(f), {}};
}

// Guess MIME type from file extension.
static std::string mime_for(const std::string& path) {
    static const std::map<std::string, std::string> types = {
        {".html",  "text/html; charset=utf-8"},
        {".css",   "text/css"},
        {".js",    "application/javascript"},
        {".json",  "application/json"},
        {".ico",   "image/x-icon"},
        {".png",   "image/png"},
        {".jpg",   "image/jpeg"},
        {".jpeg",  "image/jpeg"},
        {".svg",   "image/svg+xml"},
        {".woff2", "font/woff2"},
        {".woff",  "font/woff"},
        // audio
        {".mp3",   "audio/mpeg"},
        {".wav",   "audio/wav"},
        {".flac",  "audio/flac"},
        {".m4a",   "audio/mp4"},
        {".ogg",   "audio/ogg"},
        {".aac",   "audio/aac"},
        // video
        {".mp4",   "video/mp4"},
        {".mkv",   "video/x-matroska"},
        {".avi",   "video/x-msvideo"},
        {".mov",   "video/quicktime"},
        {".webm",  "video/webm"},
        {".m4v",   "video/mp4"},
    };
    std::string ext = fs::path(path).extension().string();
    std::transform(ext.begin(), ext.end(), ext.begin(),
                   [](unsigned char c){ return std::tolower(c); });
    auto it = types.find(ext);
    return it != types.end() ? it->second : "application/octet-stream";
}

// Sanitise a client/file path component so it can't escape the clients dir.
static std::string sanitise(const std::string& s) {
    std::string out;
    for (char c : s) {
        if (std::isalnum(static_cast<unsigned char>(c)) ||
            c == '-' || c == '_' || c == '.' || c == '/') {
            out += c;
        }
    }
    // Remove any ".." traversal
    std::string safe;
    std::istringstream ss(out);
    std::string tok;
    while (std::getline(ss, tok, '/')) {
        if (tok == ".." || tok == ".") continue;
        if (!tok.empty()) { safe += "/"; safe += tok; }
    }
    return safe;
}

// Stream a file with HTTP range-request support.
static void stream_file(const httplib::Request& req, httplib::Response& res,
                         const std::string& file_path) {
    if (!fs::exists(file_path)) { res.status = 404; return; }

    auto file_size = static_cast<long long>(fs::file_size(file_path));
    std::string mime = mime_for(file_path);

    long long byte_start = 0, byte_end = file_size - 1;

    auto range_it = req.headers.find("Range");
    bool has_range = range_it != req.headers.end();

    if (has_range) {
        // Parse "bytes=X-Y", "bytes=X-", "bytes=-Y"
        std::string range_val = range_it->second;
        if (range_val.find("bytes=") == 0) {
            range_val = range_val.substr(6);
            auto dash = range_val.find('-');
            if (dash != std::string::npos) {
                std::string s = range_val.substr(0, dash);
                std::string e = range_val.substr(dash + 1);
                if (!s.empty()) byte_start = std::stoll(s);
                if (!e.empty()) byte_end   = std::stoll(e);
            }
        }
        byte_end = std::min(byte_end, file_size - 1);
    }

    long long chunk = byte_end - byte_start + 1;

    // Read just the requested range
    std::ifstream f(file_path, std::ios::binary);
    f.seekg(byte_start);
    std::string body(static_cast<size_t>(chunk), '\0');
    f.read(body.data(), chunk);

    res.body = std::move(body);
    res.set_header("Content-Type", mime);
    res.set_header("Accept-Ranges", "bytes");
    res.set_header("Content-Length", std::to_string(chunk));

    if (has_range) {
        res.status = 206; // Partial Content
        res.set_header("Content-Range",
            "bytes " + std::to_string(byte_start) + "-" +
                       std::to_string(byte_end)   + "/" +
                       std::to_string(file_size));
    } else {
        res.status = 200;
    }
}

// Read server name from config.txt
static std::string server_name() {
    std::string path = g_base_dir + "/config.txt";
    std::string name = read_file(path);
    // strip whitespace
    name.erase(name.find_last_not_of(" \t\r\n") + 1);
    return name.empty() ? "Macro Server" : name;
}

// ── Database helpers ──────────────────────────────────────────────────────────

// Convert one SQLiteCpp column to a JSON value using the correct native type.
static json column_to_json(const SQLite::Column& col) {
    switch (col.getType()) {
        case SQLITE_INTEGER: return col.getInt64();
        case SQLITE_FLOAT:   return col.getDouble();
        case SQLITE_NULL:    return nullptr;
        default:             return col.getText();  // TEXT or BLOB → string
    }
}

static const std::map<std::string, std::pair<std::string,std::string>> DB_MAP = {
    {"music",  {"music.db",  "music"}},
    {"video",  {"video.db",  "video"}},
    {"files",  {"files.db",  "files"}},
    {"photos", {"photo.db",  "photos"}},
};

// Fetch all rows from a media table as a JSON array.
static json library_json(const std::string& media_type) {
    auto it = DB_MAP.find(media_type);
    if (it == DB_MAP.end()) return json();   // null → caller sends 404

    const std::string db_path   = g_base_dir + "/" + it->second.first;
    const std::string table     = it->second.second;

    if (!fs::exists(db_path)) return json::array();

    try {
        SQLite::Database db(db_path, SQLite::OPEN_READONLY);
        SQLite::Statement q(db, "SELECT rowid AS id, * FROM " + table);

        json arr = json::array();
        while (q.executeStep()) {
            json row;
            for (int i = 0; i < q.getColumnCount(); ++i) {
                row[q.getColumnName(i)] = column_to_json(q.getColumn(i));
            }
            arr.push_back(row);
        }
        return arr;
    } catch (const std::exception& e) {
        std::cerr << "DB error [" << media_type << "]: " << e.what() << "\n";
        return json::array();
    }
}

// Fetch file path for a given rowid from a media table.
static std::string media_path(const std::string& media_type, int id) {
    auto it = DB_MAP.find(media_type);
    if (it == DB_MAP.end()) return "";

    const std::string db_path = g_base_dir + "/" + it->second.first;
    const std::string table   = it->second.second;

    if (!fs::exists(db_path)) return "";

    try {
        SQLite::Database db(db_path, SQLite::OPEN_READONLY);
        SQLite::Statement q(db, "SELECT path FROM " + table + " WHERE rowid = ?");
        q.bind(1, id);
        if (q.executeStep()) {
            return q.getColumn(0).getText();
        }
    } catch (const std::exception& e) {
        std::cerr << "DB stream error: " << e.what() << "\n";
    }
    return "";
}

// Search a media table by name/title (and artist for music).
static json search_json(const std::string& media_type, const std::string& query) {
    auto it = DB_MAP.find(media_type);
    if (it == DB_MAP.end()) return json();

    const std::string db_path = g_base_dir + "/" + it->second.first;
    const std::string table   = it->second.second;

    if (!fs::exists(db_path)) return json::array();

    std::string like = "%" + query + "%";

    // Choose search column by type
    std::string sql;
    if (media_type == "music") {
        sql = "SELECT rowid AS id, * FROM " + table +
              " WHERE name LIKE ? OR artist LIKE ? OR album LIKE ?";
    } else {
        sql = "SELECT rowid AS id, * FROM " + table +
              " WHERE title LIKE ?";
    }

    try {
        SQLite::Database db(db_path, SQLite::OPEN_READONLY);
        SQLite::Statement q(db, sql);
        q.bind(1, like);
        if (media_type == "music") { q.bind(2, like); q.bind(3, like); }

        json arr = json::array();
        while (q.executeStep()) {
            json row;
            for (int i = 0; i < q.getColumnCount(); ++i) {
                row[q.getColumnName(i)] = column_to_json(q.getColumn(i));
            }
            arr.push_back(row);
        }
        return arr;
    } catch (const std::exception& e) {
        std::cerr << "Search error: " << e.what() << "\n";
        return json::array();
    }
}

// ── Route registration ────────────────────────────────────────────────────────

static void register_routes(httplib::Server& svr) {

    // ── GET / ──────────────────────────────────────────────────────────────
    svr.Get("/", [](const httplib::Request&, httplib::Response& res) {
        std::string body = read_file(g_clients_dir + "/dashboard.html");
        if (body.empty()) { res.status = 404; return; }
        res.set_content(body, "text/html; charset=utf-8");
    });

    // ── GET /name ──────────────────────────────────────────────────────────
    svr.Get("/name", [](const httplib::Request&, httplib::Response& res) {
        res.set_content(server_name(), "text/plain; charset=utf-8");
    });

    // ── GET /api/config ────────────────────────────────────────────────────
    svr.Get("/api/config", [](const httplib::Request&, httplib::Response& res) {
        json cfg;
        cfg["name"] = server_name();
        cfg["directories"] = json::array();

        std::string dir_path = g_base_dir + "/directory.json";
        if (fs::exists(dir_path)) {
            std::ifstream f(dir_path);
            try {
                json d = json::parse(f);
                if (d.contains("directories")) cfg["directories"] = d["directories"];
                if (d.contains("search_backend")) cfg["search_backend"] = d["search_backend"];
            } catch (...) {}
        }
        res.set_content(cfg.dump(), "application/json");
    });

    // ── GET /api/library/<type> ────────────────────────────────────────────
    svr.Get(R"(/api/library/([a-z]+))",
        [](const httplib::Request& req, httplib::Response& res) {
            std::string type = req.matches[1];
            json data = library_json(type);
            if (data.is_null()) { res.status = 404; return; }
            res.set_content(data.dump(), "application/json");
        });

    // ── GET /api/stream/<type>/<id> ────────────────────────────────────────
    svr.Get(R"(/api/stream/([a-z]+)/(\d+))",
        [](const httplib::Request& req, httplib::Response& res) {
            std::string type = req.matches[1];
            int id = std::stoi(req.matches[2]);

            if (type != "music" && type != "video") { res.status = 404; return; }

            std::string path = media_path(type, id);
            if (path.empty() || !fs::exists(path)) { res.status = 404; return; }

            stream_file(req, res, path);
        });

    // ── GET /api/search/<type>?q=... ───────────────────────────────────────
    svr.Get(R"(/api/search/([a-z]+))",
        [](const httplib::Request& req, httplib::Response& res) {
            std::string type  = req.matches[1];
            std::string query = req.has_param("q") ? req.get_param_value("q") : "";
            if (query.empty()) { res.set_content("[]", "application/json"); return; }

            json data = search_json(type, query);
            if (data.is_null()) { res.status = 404; return; }
            res.set_content(data.dump(), "application/json");
        });

    // ── GET /<client>/ ─────────────────────────────────────────────────────
    svr.Get(R"(/([a-zA-Z0-9_-]+)/)",
        [](const httplib::Request& req, httplib::Response& res) {
            std::string client = req.matches[1];
            // Don't intercept /api/ routes (regex shouldn't, but guard anyway)
            if (client == "api") { res.status = 404; return; }
            std::string path = g_clients_dir + "/" + client + "/home.html";
            std::string body = read_file(path);
            if (body.empty()) { res.status = 404; return; }
            res.set_content(body, "text/html; charset=utf-8");
        });

    // ── GET /<client>/<path> ───────────────────────────────────────────────
    svr.Get(R"(/([a-zA-Z0-9_-]+)/(.+))",
        [](const httplib::Request& req, httplib::Response& res) {
            std::string client   = req.matches[1];
            std::string filename = sanitise(req.matches[2]);
            if (client == "api") { res.status = 404; return; }

            std::string path = g_clients_dir + "/" + client + filename;
            if (!fs::exists(path) || !fs::is_regular_file(path)) {
                res.status = 404; return;
            }
            std::string body = read_file(path);
            res.set_content(body, mime_for(path));
        });
}

// ── main ─────────────────────────────────────────────────────────────────────

int main(int argc, char** argv) {
    // Resolve base directory to the directory containing this binary.
    // When run with Bazel runfiles or directly, argv[0] gives us a path.
    g_base_dir = fs::canonical(fs::path(argv[0]).parent_path()).string();
    g_clients_dir = g_base_dir + "/clients";

    // Fallback: if clients/ doesn't exist next to the binary, check common install paths
    if (!fs::exists(g_clients_dir)) {
        if (fs::exists("/usr/share/macro/clients")) {
            g_clients_dir = "/usr/share/macro/clients";
        }
    }

    // Allow overriding base dir (useful for running from repo root during dev)
    // Usage: ./macro_server [port] [base_dir]
    int port = 5000;
    if (argc >= 2) {
        try { port = std::stoi(argv[1]); } catch (...) {}
    }
    if (argc >= 3) {
        g_base_dir   = fs::canonical(argv[2]).string();
        g_clients_dir = g_base_dir + "/clients";
    }

    httplib::Server svr;
    register_routes(svr);

    // CORS for local dev
    svr.set_default_headers({
        {"Access-Control-Allow-Origin", "*"},
    });

    // Error handler
    svr.set_error_handler([](const httplib::Request& req, httplib::Response& res) {
        res.set_content(
            "{\"error\":\"" + std::to_string(res.status) + "\"}",
            "application/json"
        );
    });

    std::cout << "Macro Server (C++) listening on http://0.0.0.0:" << port << "\n";
    std::cout << "Serving from: " << g_base_dir << "\n";

    if (!svr.listen("0.0.0.0", port)) {
        std::cerr << "Failed to bind to port " << port << "\n";
        return 1;
    }

    return 0;
}
