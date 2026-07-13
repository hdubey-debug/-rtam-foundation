/* the land page: the kṣetra's own day, computed at each visit — no one updates this.
   Dateline in the mandir's script; sunrise–sunset over Jabalpur (NOAA-lite, ±2 min);
   THIS SEASON trimmed to the next three utsavas. */
function rtamLand(place){
  const D2R = Math.PI / 180, IST = 5.5;

  function sunAt(utcMs){
    const d = new Date(utcMs);
    const N = Math.floor((utcMs - Date.UTC(d.getUTCFullYear(), 0, 0)) / 86400000);
    const B = 2 * Math.PI * (N - 81) / 364;
    const eot = 9.87 * Math.sin(2 * B) - 7.53 * Math.cos(B) - 1.5 * Math.sin(B);
    const decl = 23.45 * Math.sin(2 * Math.PI * (284 + N) / 365) * D2R;
    const cosH0 = (Math.sin(-0.833 * D2R) - Math.sin(place.lat * D2R) * Math.sin(decl))
                / (Math.cos(place.lat * D2R) * Math.cos(decl));
    const H0 = Math.acos(Math.max(-1, Math.min(1, cosH0))) / D2R / 15;
    const noonUTC = 12 - place.lon / 15 - eot / 60;
    return { riseIST: noonUTC - H0 + IST, setIST: noonUTC + H0 + IST };
  }
  const fmt = h => { h = (h + 24) % 24; const m = Math.round(h * 60);
    return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0"); };

  const sun = sunAt(Date.now());
  const sunline = document.getElementById("sunline");
  if (sunline) sunline.textContent = "सूर्योदय " + fmt(sun.riseIST) + " · सूर्यास्त " + fmt(sun.setIST);

  const DG = "०१२३४५६७८९";
  const dg = n => String(n).split("").map(c => DG[+c]).join("");
  const WD = ["रविवार","सोमवार","मंगलवार","बुधवार","गुरुवार","शुक्रवार","शनिवार"];
  const MO = ["जनवरी","फ़रवरी","मार्च","अप्रैल","मई","जून","जुलाई","अगस्त","सितम्बर","अक्टूबर","नवम्बर","दिसम्बर"];
  const now = new Date();
  const dl = document.getElementById("dateline");
  if (dl) dl.textContent =
    WD[now.getDay()] + " · " + dg(now.getDate()) + " " + MO[now.getMonth()] + " " + dg(now.getFullYear());

  /* THIS SEASON: keep the next three; if nothing lies ahead, keep everything (honesty
     beats emptiness — the draft's sample dates can all be past). */
  const items = [...document.querySelectorAll(".season [data-date]")];
  const today = new Date().toISOString().slice(0, 10);
  const ahead = items.filter(li => li.dataset.date >= today);
  if (ahead.length) items.forEach(li => { if (!ahead.slice(0, 3).includes(li)) li.hidden = true; });
}
