interface DashboardTableProps {
  data: any[];
}

export default function DashboardTable({ data }: DashboardTableProps) {
  return (
    <table className="table-auto w-full border border-gray-700 bg-gray-800 text-gray-200">
      <thead className="bg-gray-700">
        <tr>
          <th className="px-3 py-2">ID</th>
          <th className="px-3 py-2">Original</th>
          <th className="px-3 py-2">Sanitized</th>
          <th className="px-3 py-2">Topic</th>
          <th className="px-3 py-2">Notices</th>
          <th className="px-3 py-2">Created</th>
          <th className="px-3 py-2">Expires</th>
        </tr>
      </thead>

      <tbody>
        {data.map((row) => (
          <tr key={row.id} className="border-t border-gray-700">
            <td className="px-3 py-2">{row.id}</td>
            <td className="px-3 py-2 whitespace-pre-line">{row.original}</td>
            <td className="px-3 py-2 whitespace-pre-line">{row.sanitized}</td>
            <td className="px-3 py-2">{row.topic}</td>
            <td className="px-3 py-2">{row.notices}</td>
            <td className="px-3 py-2">{row.created_at}</td>
            <td className="px-3 py-2">{row.expires_at}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
