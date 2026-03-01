import { getData } from "./getData";
import DashboardTable from "@/components/DashboardTable";

export default async function DashboardPage() {
  const data = await getData();

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 px-6 py-10">
      <h1 className="text-4xl font-bold mb-6">Information Manager Dashboard</h1>
      <DashboardTable data={data} />
    </div>
  );
}
