import { useEffect, useState } from "react";
import { ApiError, listEmployees, listSubordinates, type Employee, type Subordinate } from "./api";
import { EvaluationDetail } from "./components/EvaluationDetail";
import { LeaderSelector } from "./components/LeaderSelector";
import { SubordinateList } from "./components/SubordinateList";

const STORAGE_KEY = "leaderId";

function readSavedLeader(): number | null {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved ? Number(saved) : null;
}

function App() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [leaderId, setLeaderId] = useState<number | null>(readSavedLeader);
  const [subordinates, setSubordinates] = useState<Subordinate[] | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [listVersion, setListVersion] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listEmployees()
      .then(setEmployees)
      .catch(() => setError("Não foi possível carregar os funcionários."));
  }, []);

  useEffect(() => {
    if (leaderId === null) return;
    let ignore = false; // a slow answer for the previous leader must not overwrite the current one
    listSubordinates(leaderId)
      .then((data) => { if (!ignore) setSubordinates(data); })
      .catch((err) => {
        if (ignore) return;
        if (err instanceof ApiError && err.status === 404) {
          localStorage.removeItem(STORAGE_KEY); // saved leader no longer exists
          setLeaderId(null);
          setError("O líder salvo não existe mais. Escolha outro.");
        } else {
          setError("Não foi possível carregar a lista.");
        }
      });
    return () => { ignore = true; };
  }, [leaderId, listVersion]);

  function chooseLeader(id: number) {
    localStorage.setItem(STORAGE_KEY, String(id));
    setLeaderId(id);
    setSubordinates(null);
    setSelectedId(null);
    setError(null);
  }

  const selected = subordinates?.find((person) => person.id === selectedId) ?? null;

  return (
    <div className="app">
      <header className="topbar">
        <h1>Avaliação de liderados</h1>
        <LeaderSelector employees={employees} leaderId={leaderId} onChange={chooseLeader} />
      </header>

      {error && <p className="error">{error}</p>}

      {leaderId === null ? (
        <p className="muted">Escolha quem você é para ver seus liderados.</p>
      ) : (
        <main className="layout">
          <section>
            <h2>Liderados {subordinates && `(${subordinates.length})`}</h2>
            {subordinates === null ? (
              <p className="muted">Carregando…</p>
            ) : (
              <SubordinateList subordinates={subordinates} selectedId={selectedId} onSelect={setSelectedId} />
            )}
          </section>

          {selected ? (
            // key: switching person or leader starts a fresh detail (no form or data left over)
            <EvaluationDetail
              key={`${leaderId}-${selected.id}`}
              leaderId={leaderId}
              employee={selected}
              onEvaluated={() => setListVersion((current) => current + 1)}
            />
          ) : (
            subordinates && subordinates.length > 0 && (
              <p className="muted placeholder">Escolha uma pessoa para ver as avaliações.</p>
            )
          )}
        </main>
      )}
    </div>
  );
}

export default App;
