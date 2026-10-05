import type { Subordinate } from "../api";
import { formatScore, formatWeek } from "../format";

type Props = {
  subordinates: Subordinate[];
  selectedId: number | null;
  onSelect: (employeeId: number) => void;
};

export function SubordinateList({ subordinates, selectedId, onSelect }: Props) {
  if (subordinates.length === 0) {
    return <p className="muted">Ninguém abaixo de você na hierarquia.</p>;
  }

  return (
    <ul className="subordinates">
      {subordinates.map((person) => (
        <li key={person.id}>
          <button
            type="button"
            className="person"
            aria-pressed={person.id === selectedId}
            onClick={() => onSelect(person.id)}
          >
            <span className="person-main">
              <strong>{person.name}</strong>
              <span className="muted">{person.position_name}</span>
            </span>
            {person.highlight ? (
              <span className="person-side">
                <span className="score">{formatScore(person.highlight.final_score)}</span>
                <span className="muted">
                  semana de {formatWeek(person.highlight.week_start)} · {person.highlight.leader_name}
                </span>
              </span>
            ) : (
              <span className="person-side muted">Não avaliado</span>
            )}
          </button>
        </li>
      ))}
    </ul>
  );
}
