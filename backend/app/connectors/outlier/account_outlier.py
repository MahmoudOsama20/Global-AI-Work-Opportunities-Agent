import os
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import settings, DATA_DIR
from app.core.logging import app_logger

class OutlierAccountConnector:
    """Safe, read-only account inspector for Outlier worker dashboard.
    
    Security Guarantee:
    - Never collects, prompts for, or handles passwords or MFA tokens.
    - Uses local persistent browser profile where the user logs in manually.
    - Performs strictly read-only inspection of visible project allocations.
    - Never submits proposals, clicks apply, or performs financial transactions.
    """

    def __init__(self):
        self.profile_dir = DATA_DIR / "browser_profiles" / "outlier"
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    async def login_interactive(self):
        """Launches a visible browser window so the user can manually sign in to their Outlier account."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            app_logger.warning("Playwright is not installed. Run: pip install playwright && playwright install chromium")
            return {"status": "error", "message": "Playwright is not installed in the environment."}

        app_logger.info("Opening official Outlier login page. Please sign in manually in the browser window.")
        async with async_playwright() as p:
            browser_context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=False,
                args=["--start-maximized"],
            )
            page = await browser_context.new_page()
            await page.goto("https://app.outlier.ai/login")
            app_logger.info("Browser open. Please complete login and close the browser when done.")
            
            # Wait for user to close the browser or page
            try:
                await page.wait_for_close(timeout=300000)  # 5 minutes
            except Exception:
                pass
            await browser_context.close()
            return {"status": "completed", "message": "Login session stored locally in browser profile."}

    async def inspect_account(self) -> Dict[str, Any]:
        """Inspects current project allocation in the authorized account in read-only mode."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return {
                "status": "unverified",
                "is_authenticated": False,
                "active_project": None,
                "message": "Playwright browser automation module not installed.",
            }

        if not any(self.profile_dir.iterdir()):
            return {
                "status": "unverified",
                "is_authenticated": False,
                "active_project": None,
                "message": "No local browser session found. Please run 'python main.py --login-account outlier' to authenticate manually.",
            }

        try:
            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    headless=True,
                )
                page = await context.new_page()
                await page.goto("https://app.outlier.ai/en/expert/dashboard", timeout=20000)
                
                # Check if redirected to login page
                current_url = page.url
                if "login" in current_url:
                    await context.close()
                    return {
                        "status": "unverified",
                        "is_authenticated": False,
                        "active_project": None,
                        "message": "Session expired. Manual login required via 'python main.py --login-account outlier'.",
                    }

                # Read-only extraction of project name if available
                project_name = None
                try:
                    elem = await page.query_selector("[data-testid='current-project-name'], h2, h3")
                    if elem:
                        project_name = (await elem.inner_text()).strip()
                except Exception:
                    pass

                await context.close()
                return {
                    "status": "verified" if project_name else "active_session",
                    "is_authenticated": True,
                    "active_project": project_name or "Dashboard accessible (queue empty or loading)",
                    "message": "Account successfully verified in read-only mode.",
                }

        except Exception as e:
            return {
                "status": "unverified",
                "is_authenticated": False,
                "active_project": None,
                "message": f"Unable to verify account: {e}",
            }
