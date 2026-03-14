import os

from camoufox.async_api import AsyncCamoufox
from playwright_captcha import ClickSolver, CaptchaType, FrameworkType
from playwright_captcha.utils.camoufox_add_init_script.add_init_script import (
    get_addon_path,
)
from execution.login.dom_interaction.interfaces.dom_interaction_interface import (
    DomInteractionInterface,
)


class DomInteractionDriver(DomInteractionInterface):

    async def __aenter__(self):
        self._camoufox = AsyncCamoufox(
            headless="virtual",
            geoip=True,
            humanize=True,
            main_world_eval=True,
            addons=[os.path.abspath(get_addon_path())],
        )
        self._browser = await self._camoufox.__aenter__()
        self._page = await self._browser.new_page()
        await self._page.goto(self._url)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._camoufox.__aexit__(exc_type, exc, tb)
        return False

    async def disconnect_driver(self):
        await self._browser.close()

    async def get_current_url(self) -> str:
        return self._page.url

    async def get_page_html(self) -> str:
        return await self._page.content()

    async def is_element_visible(self, xpath: str) -> bool:
        element = self._page.locator(f"xpath={xpath}")
        return await element.count() > 0 and await element.first.is_visible()

    async def save_screenshot(self, screenshot_id: str):
        if screenshot_id is None:
            return

        path = "/config/images"
        await self._page.locator("body").screenshot(
            path=os.path.join(path, f"{screenshot_id}.png")
        )

    async def find_element(self, xpath: str) -> bool:
        return await self._page.locator(f"xpath={xpath}").count() > 0

    async def solve_captcha(self):
        """Attempt to solve captchas on the page using click-based solving."""
        captcha_types = [
            CaptchaType.CLOUDFLARE_TURNSTILE,
            CaptchaType.CLOUDFLARE_INTERSTITIAL,
        ]

        for captcha_type in captcha_types:
            try:
                async with ClickSolver(
                    framework=FrameworkType.CAMOUFOX,
                    page=self._page,
                    max_attempts=3,
                    attempt_delay=2,
                ) as solver:
                    await solver.solve_captcha(
                        captcha_container=self._page,
                        captcha_type=captcha_type,
                    )
                    return
            except Exception:
                continue

    async def fill_text(self, xpath: str, value: str):
        await self._page.locator(f"xpath={xpath}").fill(value)

    async def click_button(self, xpath: str):
        await self._page.locator(f"xpath={xpath}").click()

    async def open_url(self, url: str):
        await self._page.goto(url)

    async def wait(self, ms: int):
        await self._page.wait_for_timeout(ms)
