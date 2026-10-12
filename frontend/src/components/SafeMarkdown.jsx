/** Small, safe Markdown renderer: all content is emitted as React text nodes. */
import React from "react";

function inline(text, keyPrefix) {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={`${keyPrefix}-${index}`}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("`") && part.endsWith("`")) return <code key={`${keyPrefix}-${index}`}>{part.slice(1, -1)}</code>;
    return part;
  });
}

export default function SafeMarkdown({ source }) {
  return source.split(/\n{2,}/).map((block, index) => {
    const lines = block.split("\n");
    const heading = lines[0].match(/^(#{1,3})\s+(.*)$/);
    if (heading) { const Tag = `h${heading[1].length}`; return <Tag key={index}>{inline(heading[2], `h${index}`)}</Tag>; }
    if (lines.every((line) => /^\s*[-*]\s+/.test(line))) return <ul key={index}>{lines.map((line, i) => <li key={i}>{inline(line.replace(/^\s*[-*]\s+/, ""), `l${index}-${i}`)}</li>)}</ul>;
    return <p key={index}>{lines.map((line, i) => <React.Fragment key={i}>{i > 0 && <br />}{inline(line, `p${index}-${i}`)}</React.Fragment>)}</p>;
  });
}
