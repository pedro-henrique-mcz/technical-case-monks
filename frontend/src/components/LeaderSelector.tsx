import type { Employee } from "../api";

type Props = {
  employees: Employee[];
  leaderId: number | null;
  onChange: (leaderId: number) => void;
};

export function LeaderSelector({ employees, leaderId, onChange }: Props) {
  return (
    <label className="leader-selector">
      Você é
      <select value={leaderId ?? ""} onChange={(e) => onChange(Number(e.target.value))}>
        <option value="" disabled>Escolha um líder</option>
        {employees.map((employee) => (
          <option key={employee.id} value={employee.id}>{employee.name}</option>
        ))}
      </select>
    </label>
  );
}
