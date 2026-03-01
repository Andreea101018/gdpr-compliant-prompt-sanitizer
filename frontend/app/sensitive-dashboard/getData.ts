export async function getData() {
  const res = await fetch("http://127.0.0.1:5000/api/data", {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch data");
  return res.json();
}
