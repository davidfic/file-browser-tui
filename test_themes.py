#!/usr/bin/env python3
"""Test script for theme switching in file browser TUI."""

import asyncio
from pathlib import Path
from textual.app import App
from textual.widgets import Static
from main import FileBrowserApp, CUSTOM_THEMES


async def test_theme_registration():
    """Test that all custom themes are registered properly."""
    print("Testing theme registration...")
    app = FileBrowserApp()

    # Check that all themes are registered
    for theme_name in CUSTOM_THEMES.keys():
        assert theme_name in app.available_themes, f"Theme {theme_name} not registered"

    print(f"✓ All {len(CUSTOM_THEMES)} custom themes registered successfully")
    return True


async def test_theme_switching():
    """Test that theme switching works without errors."""
    print("\nTesting theme switching...")
    app = FileBrowserApp()

    # Try switching to each theme
    for theme_name in CUSTOM_THEMES.keys():
        try:
            app.theme = theme_name
            assert app.theme == theme_name, f"Failed to set theme to {theme_name}"
            print(f"✓ Successfully switched to theme: {theme_name}")
        except Exception as e:
            print(f"✗ Error switching to theme {theme_name}: {e}")
            return False

    print(f"✓ All theme switches successful")
    return True


async def test_default_theme():
    """Test that the default theme is set correctly."""
    print("\nTesting default theme...")
    app = FileBrowserApp()

    assert app.theme == "tokyo-night", f"Expected default theme 'tokyo-night', got '{app.theme}'"
    print(f"✓ Default theme set correctly: {app.theme}")
    return True


async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("File Browser TUI - Theme Switching Tests")
    print("=" * 60)

    tests = [
        ("Theme Registration", test_theme_registration),
        ("Theme Switching", test_theme_switching),
        ("Default Theme", test_default_theme),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    exit(exit_code)
