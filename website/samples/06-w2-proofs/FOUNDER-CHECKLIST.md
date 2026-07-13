# The 2-minute real-device check (for the founder)

This cluster cannot run WebKit (Safari's engine) — no sudo for its system
libraries — so Safari is proven on real devices, by you. Run this once per
release, after the site is reachable (locally: `python3 -m http.server -d
website/dist` on your machine, or the live URL once Pages is up).

## iPhone · Safari (~1 min)

1. Open the site. The temple render should paint **immediately** — no blank
   band, no curtain effect over it.
2. Swipe down the landing. No sideways scrolling anywhere.
3. Tap **मंदिर में प्रवेश · ENTER**. The header mark should change chakra →
   anāhata once, then stay still.
4. The walk: swipe the dark band **left** — east, south, west, north — the
   little compass dot should travel with you.
5. Through **गर्भगृह** door: scroll the approach — the wheel should shed its
   rim, fold its petals, end at the gold point. Tap the breathing point at
   the very bottom: you should land back on the land page.
6. Tap **MENU** — it should fill the screen, and CLOSE should close it.

## Windows · Chrome or Edge (~40 s)

1. Open the site, press `Tab` a few times — a visible outline should move
   through the links (skip link first).
2. Landing → ENTER → walk (mouse wheel over the dark band should move it
   clockwise) → गर्भगृह → approach → point → land.

## If anything fails

Note the device, browser, and step number, and send it back — nothing else
needed. (iOS Settings → Accessibility → Motion → "Reduce Motion" ON, then
reload /darshana/: you should see all three figures stacked — chakra,
anāhata, bindu — with all three captions, and no animation.)
