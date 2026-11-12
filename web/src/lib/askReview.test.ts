import { describe, expect, it } from "vitest";
import { differingIndices } from "./ask";

// Reviewer: positions from the server are batch_key positions (separators removed),
// but the choice cards index into the raw listed string, which can keep a hyphen.
describe("differingIndices with a separator before the differing character", () => {
  it("highlights the O in the listed raw batch", () => {
    const listed = "MZP-25O2"; // batch_key MZP25O2, differs from pack at key position 6
    const pack = "MZP2502";
    const diff = differingIndices(listed, pack, [6]);
    const marked = [...listed].filter((_, i) => diff.has(i)).join("");
    expect(marked).toBe("O");
  });
});
