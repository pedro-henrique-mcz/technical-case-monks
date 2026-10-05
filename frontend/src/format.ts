// "2026-10-05" is a calendar date, not an instant. new Date("2026-10-05") reads it as midnight UTC,
// which is still the day before in Brazil, so the text is split instead.
export function formatWeek(weekStart: string): string {
  const [year, month, day] = weekStart.split("-");
  return `${day}/${month}/${year}`;
}

export function formatScore(score: number): string {
  return score.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
