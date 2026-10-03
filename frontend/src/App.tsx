import { useEffect, useState } from "react";
import { listEmployees, listSubordinates, type Employee } from "./api";

const STORAGE_KEY = "leaderId";

function App() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [leaderId, setLeaderId] = useState<number | null>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? Number(saved) : null;
  });
  const [subordinates, setSubordinates] = useState<Employee[]>([]);

  useEffect(() => {
    listEmployees().then(setEmployees);
  }, []);

  useEffect(() => {
    if (leaderId === null) return;
    localStorage.setItem(STORAGE_KEY, String(leaderId));
    listSubordinates(leaderId).then(setSubordinates);
  }, [leaderId]);

  return (
    <main>
      <h1>Monks Evaluation</h1>
      <label>
        Leader:{" "}
        <select
          value={leaderId ?? ""}
          onChange={(e) => setLeaderId(Number(e.target.value))}
        >
          <option value="" disabled>Choose a leader</option>
          {employees.map((e) => (
            <option key={e.id} value={e.id}>{e.name}</option>
          ))}
        </select>
      </label>
      <h2>Subordinates ({subordinates.length})</h2>
      <ul>
        {subordinates.map((e) => (
          <li key={e.id}>{e.name}</li>
        ))}
      </ul>
    </main>
  );
}

export default App;