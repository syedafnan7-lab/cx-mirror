"""
CX MIRROR — Live DOM Extractor
Extracts exact bounding boxes, computed styles, text, and semantic roles using Playwright CDP.
Strictly adheres to rendering_config.json for reproducible capture.
"""

import os
import json
import hashlib
import time
from typing import Dict, Any, Tuple, Optional
from playwright.async_api import async_playwright, Page, BrowserContext

from app.models.graph_models import GraphNode, BoundingBox, SpatialGraph


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "rendering_config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    RENDERING_CONFIG = json.load(f)

CONFIG_HASH = hashlib.sha256(json.dumps(RENDERING_CONFIG, sort_keys=True).encode()).hexdigest()[:12]


JS_DOM_EXTRACTION_SCRIPT = """
() => {
    const nodes = [];
    const elements = document.querySelectorAll(
        '[data-role], h1, h2, h3, p, button, a, span.current-price, span.original-price, span.discount-badge, .legal-disclaimer-text, svg.product-hero-svg'
    );

    let counter = 0;
    elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.width <= 0 && rect.height <= 0) return;

        const style = window.getComputedStyle(el);
        const isVisible = style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity || '1') > 0.01;

        // Semantic Role extraction
        const role = el.getAttribute('data-role') || el.getAttribute('role') || '';
        let elementType = 'text';
        if (el.tagName === 'BUTTON' || role === 'checkout_button' || el.classList.contains('checkout-btn')) {
            elementType = 'button';
        } else if (role === 'current_price' || el.classList.contains('current-price')) {
            elementType = 'price';
        } else if (role === 'original_price' || el.classList.contains('original-price')) {
            elementType = 'price';
        } else if (role === 'legal_disclaimer' || el.classList.contains('legal-disclaimer-text')) {
            elementType = 'legal';
        } else if (role === 'product_image' || el.tagName === 'SVG' || el.tagName === 'IMG') {
            elementType = 'image';
        } else if (role === 'discount_badge') {
            elementType = 'badge';
        }

        // Determine node importance
        let importance = 1.0;
        if (elementType === 'price' || elementType === 'legal') {
            importance = 3.0;
        } else if (elementType === 'button' || role === 'checkout_button') {
            importance = 2.0;
        } else if (role === 'product_title' || role === 'product_image' || role === 'sku') {
            importance = 1.5;
        }

        const id = role ? `dom_${role}` : `dom_el_${counter++}_${el.tagName.toLowerCase()}`;

        // Get immediate visible text (not entire subtree if nested)
        let textContent = '';
        if (el.childNodes.length > 0) {
            for (let i = 0; i < el.childNodes.length; i++) {
                if (el.childNodes[i].nodeType === Node.TEXT_NODE) {
                    textContent += el.childNodes[i].textContent;
                }
            }
            textContent = textContent.trim();
        }
        if (!textContent) {
            textContent = (el.textContent || '').trim();
        }

        nodes.push({
            id: id,
            role: role || null,
            element_type: elementType,
            importance: importance,
            text: textContent,
            bounding_box: {
                x: Math.round(rect.x * 100) / 100,
                y: Math.round(rect.y * 100) / 100,
                width: Math.round(rect.width * 100) / 100,
                height: Math.round(rect.height * 100) / 100
            },
            font_size: parseFloat(style.fontSize) || 16.0,
            font_weight: style.fontWeight || '400',
            color: style.color || '#000000',
            background_color: style.backgroundColor || 'transparent',
            z_index: parseInt(style.zIndex, 10) || 0,
            opacity: parseFloat(style.opacity || '1.0'),
            visibility: isVisible
        });
    });

    return nodes;
}
"""


async def extract_dom_graph_from_url(
    target_url: str,
    screenshot_save_path: Optional[str] = None
) -> Tuple[SpatialGraph, bytes, Dict[str, Any]]:
    """
    Launches Playwright with controlled rendering parameters, captures live screenshot,
    and extracts deterministic DOM spatial graph.
    """
    start_time = time.time()
    vp = RENDERING_CONFIG.get("viewport", {"width": 1440, "height": 1000})

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--font-render-hinting=none",
                "--disable-lcd-text"
            ]
        )

        context = await browser.new_context(
            viewport={"width": vp["width"], "height": vp["height"]},
            device_scale_factor=RENDERING_CONFIG.get("device_scale_factor", 1),
            color_scheme=RENDERING_CONFIG.get("color_scheme", "light"),
            locale=RENDERING_CONFIG.get("locale", "en-US"),
            timezone_id=RENDERING_CONFIG.get("timezone", "UTC"),
            reduced_motion=RENDERING_CONFIG.get("reduced_motion", "reduce"),
        )

        page = await context.new_page()

        # Invalidate CSS animations and transitions for rock-solid stability
        if RENDERING_CONFIG.get("animations_disabled", True):
            await page.add_init_script("""
                const style = document.createElement('style');
                style.innerHTML = `
                    *, *::before, *::after {
                        transition-duration: 0s !important;
                        animation-duration: 0s !important;
                        caret-color: transparent !important;
                    }
                `;
                document.documentElement.appendChild(style);
            """)

        await page.goto(target_url, wait_until="networkidle")

        # Wait for document.fonts.ready
        font_timeout = RENDERING_CONFIG.get("font_wait_timeout_ms", 10000)
        try:
            await page.wait_for_function("() => document.fonts.ready", timeout=font_timeout)
        except Exception:
            pass

        # Brief settle time for layout stabilization
        await page.wait_for_timeout(250)

        # Extract DOM elements
        raw_nodes = await page.evaluate(JS_DOM_EXTRACTION_SCRIPT)

        # Capture screenshot
        screenshot_bytes = await page.screenshot(
            full_page=False,
            clip={"x": 0, "y": 0, "width": vp["width"], "height": vp["height"]}
        )

        if screenshot_save_path:
            os.makedirs(os.path.dirname(os.path.abspath(screenshot_save_path)), exist_ok=True)
            with open(screenshot_save_path, "wb") as f:
                f.write(screenshot_bytes)

        browser_version = browser.version
        await context.close()
        await browser.close()

    # Construct SpatialGraph
    graph_nodes: Dict[str, GraphNode] = {}
    for item in raw_nodes:
        nid = item["id"]
        # De-duplicate if needed
        if nid in graph_nodes:
            nid = f"{nid}_{len(graph_nodes)}"

        node = GraphNode(
            id=nid,
            element_type=item["element_type"],
            role=item.get("role"),
            text=item.get("text", ""),
            bounding_box=BoundingBox(**item["bounding_box"]),
            font_size=item.get("font_size"),
            font_weight=item.get("font_weight"),
            color=item.get("color"),
            background_color=item.get("background_color"),
            z_index=item.get("z_index", 0),
            opacity=item.get("opacity", 1.0),
            visibility=item.get("visibility", True),
            importance=item.get("importance", 1.0)
        )
        graph_nodes[nid] = node

    graph = SpatialGraph(nodes=graph_nodes, viewport=vp)

    rendering_meta = {
        "browser": "chromium",
        "browser_version": browser_version,
        "viewport": vp,
        "device_scale_factor": RENDERING_CONFIG.get("device_scale_factor", 1),
        "rendering_config_hash": CONFIG_HASH,
        "font_readiness": True,
        "timestamp": time.time(),
        "duration_ms": round((time.time() - start_time) * 1000, 2)
    }

    return graph, screenshot_bytes, rendering_meta

