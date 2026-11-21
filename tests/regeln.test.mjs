// Runs the rules of docs/app/index.html outside a browser: node --test tests/
// The page script is loaded into a sandbox with a minimal stand-in for the DOM.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const html = readFileSync(new URL("../docs/app/index.html", import.meta.url), "utf8");
const code = html.slice(html.lastIndexOf("<script>") + 8, html.lastIndexOf("</script>"));

function page() {
  const els = {};
  const el = () => ({ value: "", textContent: "", checked: false, hidden: false, disabled: false, children: [],
    appendChild(c) { this.children.push(c); return c; }, addEventListener() {}, setAttribute() {}, focus() {} });
  const document = { getElementById: id => (els[id] ??= el()), createElement: el, createTextNode: el };
  const ctx = vm.createContext({ document, window: {}, console });
  vm.runInContext(code + "\n;globalThis.t = { weg, stelle, entscheide, zustaendig, antraege, abw, P, protokoll, anrufWerkzeuge, setWer: function (w) { anrufWer = w; } };", ctx);
  return ctx.t;
}
const find = (t, nr) => t.antraege.find(q => q.nr === nr);

test("the amount decides how many people approve", () => {
  const t = page();
  assert.deepEqual([...t.weg(820, "4100", "hartmann").rollen], ["KST"]);
  assert.deepEqual([...t.weg(8400, "4100", "hartmann").rollen], ["KST", "BL"]);
  assert.deepEqual([...t.weg(18600, "6300", "arnold").rollen], ["KST", "BL", "FIN"]);
  assert.deepEqual([...t.weg(64000, "6300", "arnold").rollen], ["KST", "BL", "FIN", "GF"]);
});

test("nobody approves their own request", () => {
  const t = page();
  const w = t.weg(3200, "5200", "kaya");            // head of the cost centre asks herself
  assert.deepEqual([...w.rollen], ["BL"]);
  assert.equal(w.entfallen, true);
  assert.deepEqual([...t.weg(500, "5200", "kaya").rollen], ["BL"]);   // no step left: the next one up decides
});

test("only the person in charge can decide, and only once", () => {
  const t = page();
  const q = t.stelle("hartmann", "4100", "Hubwagen", 8400, Date.now());
  assert.equal(t.entscheide(q, "vogt", true, "", Date.now()), false);    // not her turn yet
  assert.equal(t.entscheide(q, "weber", true, "", Date.now()), true);
  assert.equal(t.entscheide(q, "weber", true, "", Date.now()), false);   // no second signature
  assert.equal(t.entscheide(q, "vogt", true, "", Date.now()), true);
  assert.equal(q.status, "frei");
});

test("absence hands over to the deputy, unless the deputy is part of the request", () => {
  const t = page();
  const q = t.stelle("hartmann", "4100", "Hubwagen", 8400, Date.now());
  t.entscheide(q, "weber", true, "", Date.now());
  t.abw.vogt = true;
  assert.equal(t.zustaendig(q).person, "brandt");
  assert.equal(t.zustaendig(q).vertritt, "vogt");
  const big = find(t, "BA-1044");                    // 64.000 €, last step is Keller
  t.entscheide(big, "lindner", true, "", Date.now());
  t.entscheide(big, "brandt", true, "", Date.now());
  t.abw.sommer = true;                               // finance absent, deputy Keller holds the last step himself
  assert.ok(t.zustaendig(big).gesperrt);
});

test("the call can do exactly what the person on the phone may do", () => {
  const t = page();
  t.setWer("vogt");
  assert.match(t.anrufWerkzeuge.offene_freigaben(), /warten 2 Anträge/);
  assert.match(t.anrufWerkzeuge.freigeben({ nummer: "BA-1044" }), /Nicht ausgeführt/);      // lies with Lindner
  assert.match(t.anrufWerkzeuge.ablehnen({ nummer: "BA-1045", grund: "" }), /Begründung/);
  assert.match(t.anrufWerkzeuge.freigeben({ nummer: "BA 1045" }), /freigegeben, der Antrag ist damit durch/);
  assert.equal(find(t, "BA-1045").status, "frei");
  assert.match(t.anrufWerkzeuge.freigeben({ nummer: "BA-1045" }), /Nicht ausgeführt/);      // not twice
  assert.match(t.protokoll[0].was, /Per Anruf bestätigt/);
});
