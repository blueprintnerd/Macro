#include <ftxui/dom/elements.hpp>
#include <ftxui/screen/screen.hpp>
#include <iostream>

int main() {
  using namespace ftxui;

  auto document = vbox({
      text("Macro CLI") | ftxui::bold | center,
      separator(),
      hbox({
          text(" Search: "),
          text("Type your query here...") | dim,
      }) | border,
  });

  auto screen = Screen::Create(Dimension::Full(), Dimension::Fit(document));
  Render(screen, document);

  std::cout << screen.ToString() << std::endl;

  return 0;
}
