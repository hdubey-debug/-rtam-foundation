export default function TopBar() {
  return (
    <header className="pointer-events-none absolute inset-x-0 top-0 z-10 flex items-baseline justify-between px-6 py-4">
      <div className="flex items-baseline gap-4">
        <span className="font-deva text-xl text-bhasma">ऋतम्भरेश्वर मंदिर</span>
        <span className="font-display text-[11px] font-semibold uppercase tracking-[0.28em] text-gold">
          Rtambhareshvara Mandir
        </span>
      </div>
      <span className="font-body text-[11px] text-bhasma-deep">
        parametric design study — not for construction
      </span>
    </header>
  );
}
