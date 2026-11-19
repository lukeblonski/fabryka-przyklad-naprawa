// Formularz zapisu na listę: wysyła e-mail do POST /zapisz (serwer.py) i pokazuje wynik pod formularzem.
document.getElementById("zapis").addEventListener("submit", async (zdarzenie) => {
  zdarzenie.preventDefault();
  const wynik = document.getElementById("wynik");
  const email = zdarzenie.target.email.value;
  try {
    const odpowiedz = await fetch("zapisz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    wynik.textContent = odpowiedz.ok ? `Zapisane: ${email}. Napiszemy, gdy otworzymy drugi warsztat.` : "Nie udało się zapisać. Spróbuj później.";
  } catch (blad) {
    wynik.textContent = "Nie udało się zapisać. Spróbuj później.";
  }
});
