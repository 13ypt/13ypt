import type { Actor, ActorId } from "../data/types";

interface Props {
  actors: Actor[];
  enabled: Set<ActorId>;
  onToggle: (id: ActorId) => void;
  onAll: () => void;
  onNone: () => void;
}

export default function ActorFilter({
  actors,
  enabled,
  onToggle,
  onAll,
  onNone,
}: Props) {
  if (!actors.length) return null;
  return (
    <div className="actor-filter">
      <div className="actor-filter-head">
        <span className="actor-filter-label">人物でフィルタ</span>
        <button className="reset-btn" onClick={onAll}>
          全選択
        </button>
        <button className="reset-btn" onClick={onNone}>
          解除
        </button>
      </div>
      <div className="actor-filter-list">
        {actors.map((a) => (
          <label key={a.id} className="actor-toggle">
            <input
              type="checkbox"
              checked={enabled.has(a.id)}
              onChange={() => onToggle(a.id)}
            />
            <span>{a.nameJa}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
