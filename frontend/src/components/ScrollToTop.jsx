import { useEffect } from "react";
import { useLocation } from "react-router-dom";

/**
 * ScrollToTop automatically scrolls the window and main page containers
 * to the very top whenever the route / pathname changes.
 */
export default function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    // Scroll window to top instantly
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: "instant",
    });

    // Also reset root document scroll positions
    if (document.documentElement) {
      document.documentElement.scrollTop = 0;
    }
    if (document.body) {
      document.body.scrollTop = 0;
    }

    // Reset potential scrollable container elements
    const appMain = document.querySelector(".app-main");
    if (appMain) {
      appMain.scrollTop = 0;
    }

    const pageContent = document.querySelector(".page-content");
    if (pageContent) {
      pageContent.scrollTop = 0;
    }
  }, [pathname]);

  return null;
}
