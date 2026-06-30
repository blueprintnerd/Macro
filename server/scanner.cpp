#include <algorithm>
#include <cctype>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include <SQLiteCpp/SQLiteCpp.h>
#include <nlohmann/json.hpp>

namespace fs = std::filesystem;

void scan_directory(const std::string& path, SQLite::Database& music_db, SQLite::Database& video_db) {
    static const std::vector<std::string> music_exts = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"};
    static const std::vector<std::string> video_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"};

    SQLite::Transaction music_transaction(music_db);
    SQLite::Transaction video_transaction(video_db);

    SQLite::Statement music_query(music_db, "INSERT OR IGNORE INTO music (name, path, artist, album, playlist, number, play_count, lyrics) VALUES (?, ?, 'Unknown Artist', 'Unknown Album', 'Default', 0, 0, '')");
    SQLite::Statement video_query(video_db, "INSERT OR IGNORE INTO video (title, path, creator, resolution, number, play_count) VALUES (?, ?, 'Unknown Creator', 'Unknown', 0, 0)");

    for (const auto& entry : fs::recursive_directory_iterator(path, fs::directory_options::skip_permission_denied)) {
        try {
            if (entry.is_regular_file()) {
                std::string ext = entry.path().extension().string();
                std::transform(ext.begin(), ext.end(), ext.begin(), [](unsigned char c) { return std::tolower(c); });
                
                std::string filename = entry.path().filename().stem().string();
                std::string full_path = fs::absolute(entry.path()).string();
                
                if (std::find(music_exts.begin(), music_exts.end(), ext) != music_exts.end()) {
                    music_query.bind(1, filename);
                    music_query.bind(2, full_path);
                    music_query.executeStep();
                    music_query.reset();
                    music_query.clearBindings();
                } else if (std::find(video_exts.begin(), video_exts.end(), ext) != video_exts.end()) {
                    video_query.bind(1, filename);
                    video_query.bind(2, full_path);
                    video_query.executeStep();
                    video_query.reset();
                    video_query.clearBindings();
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "Error scanning " << entry.path() << ": " << e.what() << std::endl;
        }
    }
    
    music_transaction.commit();
    video_transaction.commit();
}

int main(int argc, char** argv) {
    std::string base_dir = ".";
    if (argc > 1) {
        base_dir = argv[1];
    }
    
    std::string config_file = base_dir + "/directory.json";

    std::ifstream f(config_file);
    if (!f.is_open()) {
        std::cerr << "Could not open " << config_file << std::endl;
        return 1;
    }
    nlohmann::json data;
    try {
        data = nlohmann::json::parse(f);
    } catch (const nlohmann::json::parse_error& e) {
        std::cerr << "JSON parse error: " << e.what() << std::endl;
        return 1;
    }
    
    if (!data.contains("directories") || !data["directories"].is_array()) {
        std::cerr << "Invalid config: 'directories' array missing." << std::endl;
        return 1;
    }

    try {
        SQLite::Database music_db(base_dir + "/music.db", SQLite::OPEN_READWRITE | SQLite::OPEN_CREATE);
        SQLite::Database video_db(base_dir + "/video.db", SQLite::OPEN_READWRITE | SQLite::OPEN_CREATE);

        music_db.exec("CREATE TABLE IF NOT EXISTS music(name TEXT, path TEXT UNIQUE, artist TEXT, album TEXT, playlist TEXT, number INTEGER, play_count INTEGER, lyrics TEXT)");
        video_db.exec("CREATE TABLE IF NOT EXISTS video(title TEXT, path TEXT UNIQUE, creator TEXT, resolution TEXT, number INTEGER, play_count INTEGER)");

        for (const auto& dir : data["directories"]) {
            if (!dir.is_string()) continue;
            std::string dir_str = dir.get<std::string>();
            if (fs::exists(dir_str) && fs::is_directory(dir_str)) {
                std::cout << "Scanning: " << dir_str << std::endl;
                scan_directory(dir_str, music_db, video_db);
            } else {
                std::cerr << "Path is not a directory or does not exist: " << dir_str << std::endl;
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "SQLite error: " << e.what() << std::endl;
        return 1;
    }

    std::cout << "Scan complete (C++ backend)." << std::endl;
    return 0;
}
