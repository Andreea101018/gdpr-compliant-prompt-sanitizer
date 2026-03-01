"use client";

import React, { useEffect, useState } from "react";
import TopNav from "@/components/TopNav";

type Entry = {
  id: number;
  topic: string;
  original: string | null;
  sanitized: string | null;
  reformulated: string | null;
  notices: any;
  created_at: string;
  expires_at: string;
  retention: string;
};

//
// MODAL POPUP
//
function ConversationModal({
  entry,
  onClose,
  onDelete,
  onUpdateRetention,
}: {
  entry: Entry;
  onClose: () => void;
  onDelete: (id: number) => void;
  onUpdateRetention: (id: number, retention: string) => void;
}) {
  if (!entry) return null;

  //
  // RETENTION LOGIC
  //
  const presetValues = ["7d", "30d", "90d", "365d"];

  const initialMode = presetValues.includes(entry.retention)
    ? entry.retention
    : "custom";

  const [mode, setMode] = useState(initialMode);
  const [customDays, setCustomDays] = useState(
    initialMode === "custom" ? entry.retention.replace("d", "") : ""
  );
  const [customError, setCustomError] = useState<string | null>(null);

  function validateCustom(value: string) {
    if (!value) {
      setCustomError("Enter a number between 1 and 365.");
      return false;
    }
    const num = Number(value);
    if (num < 1 || num > 365) {
      setCustomError("Retention must be between 1 and 365 days.");
      return false;
    }
    setCustomError(null);
    return true;
  }

  function sendRetention() {
    if (mode === "custom") {
      if (!validateCustom(customDays)) return;
      onUpdateRetention(entry.id, `${customDays}d`);
    } else {
      onUpdateRetention(entry.id, mode);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[#11171f] w-[900px] max-w-[95%] max-height-[85vh] overflow-y-auto rounded-2xl border border-[#1c2128] shadow-2xl p-10">
        <h2 className="text-3xl font-bold text-blue-400 mb-8">
          Conversation Details
        </h2>

        <div className="space-y-8">
          {/* MESSAGE */}
          <div>
            <h3 className="text-sm text-gray-400 mb-2 font-semibold">Conversation</h3>
            <p className="text-gray-200 text-lg whitespace-pre-line bg-[#1a202c] p-6 rounded-xl border border-[#2b3240]">
              {entry.reformulated ?? entry.sanitized ?? entry.original}
            </p>
          </div>

          {/* NOTICES */}
          {entry.original === null && entry.notices && (
            <div>
              <h3 className="text-sm text-red-400 font-semibold mb-2">Sensitive Elements</h3>
              <div className="space-y-3">
                {JSON.parse(entry.notices).map((n: any, i: number) => (
                  <div
                    key={i}
                    className="bg-red-900/20 border border-red-700/40 rounded-xl px-6 py-4 text-gray-200"
                  >
                    <p className="font-bold text-red-300 text-lg">• {n.type}</p>
                    <p>Category: {n.gdpr_category}</p>
                    <p>Detected: {n.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* DATES */}
          <div className="grid grid-cols-2 gap-10">
            <div>
              <h3 className="text-sm text-gray-400 mb-1">Stored</h3>
              <p className="text-gray-300">
                {new Date(entry.created_at).toLocaleString()}
              </p>
            </div>

            <div>
              <h3 className="text-sm text-gray-400 mb-1">Expires</h3>
              <p className="text-gray-300">
                {new Date(entry.expires_at).toLocaleString()}
              </p>
            </div>
          </div>

          {/* RETENTION */}
          <div className="w-60">
            <h3 className="text-sm text-gray-400 mb-2">Retention</h3>

            {/* Preset Selector */}
            <select
              className="bg-[#1a202c] text-gray-200 border border-gray-700 rounded-lg px-4 py-2 w-full"
              value={mode}
              onChange={(e) => {
                const value = e.target.value;
                setMode(value);

                if (value !== "custom") {
                  setCustomDays("");
                  setCustomError(null);
                  onUpdateRetention(entry.id, value);
                }
              }}
            >
              <option value="7d">7 days</option>
              <option value="30d">30 days</option>
              <option value="90d">90 days</option>
              <option value="365d">1 year</option>
              <option value="custom">Custom…</option>
            </select>

            {/* Custom Input */}
            {mode === "custom" && (
              <div className="mt-3 flex items-center gap-3">
                <input
                  type="number"
                  min={1}
                  max={365}
                  value={customDays}
                  placeholder="Days"
                  onChange={(e) => {
                    const val = e.target.value;
                    setCustomDays(val);
                    if (validateCustom(val)) {
                      onUpdateRetention(entry.id, `${val}d`);
                    }
                  }}
                  className="bg-[#1a202c] border border-gray-700 rounded-lg px-4 py-2 w-24 text-gray-200"
                />

                {/* Days label */}
                <span className="text-gray-400">days</span>

                {customError && (
                  <p className="text-red-400 text-xs mt-1">{customError}</p>
                )}
              </div>
            )}
          </div>

          {/* DELETE */}
          <button
            onClick={() => onDelete(entry.id)}
            className="text-red-400 hover:text-red-300 text-lg font-semibold"
          >
            Delete Conversation
          </button>

          {/* CLOSE */}
          <div className="flex justify-end mt-6">
            <button
              onClick={onClose}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-lg transition"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

//
// MAIN DASHBOARD PAGE
//
export default function DashboardPage() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [topics, setTopics] = useState<string[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [modalEntry, setModalEntry] = useState<Entry | null>(null);

  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [selectAll, setSelectAll] = useState(false);

  async function loadData() {
    const res = await fetch("http://localhost:5000/api/data");
    const data = (await res.json()) as Entry[];
    setEntries(data);

    const topicList = [...new Set(data.map((e) => e.topic))];
    setTopics(topicList);

    if (!selectedTopic && topicList.length > 0) {
      setSelectedTopic(topicList[0]);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function toggleSelect(id: number) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  function toggleSelectAllRows() {
    if (selectAll) {
      setSelectedIds([]);
      setSelectAll(false);
    } else {
      const allIds = filtered.map((e) => e.id);
      setSelectedIds(allIds);
      setSelectAll(true);
    }
  }

  async function deleteSelected() {
    for (const id of selectedIds) {
      await fetch(`http://localhost:5000/api/delete/${id}`, {
        method: "DELETE",
      });
    }
    setSelectedIds([]);
    setSelectAll(false);
    loadData();
  }

  async function deleteEntry(id: number) {
    await fetch(`http://localhost:5000/api/delete/${id}`, {
      method: "DELETE",
    });
    setModalEntry(null);
    loadData();
  }

  async function updateRetention(id: number, retention: string) {
    await fetch(`http://localhost:5000/api/update/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ retention }),
    });
    loadData();
  }

  const filtered = entries.filter((e) => e.topic === selectedTopic);

  return (
    <>
      <TopNav />

      <div className="flex min-h-screen bg-[#0d1117] text-gray-100">
        {/* SIDEBAR */}
        <aside className="w-64 bg-[#11171f] border-r border-[#1c2128] p-6">
          <h2 className="text-xl font-bold text-blue-400 mb-4">Topics</h2>

          <div className="space-y-2">
            {topics.map((topic) => (
              <button
                key={topic}
                onClick={() => {
                  setSelectedTopic(topic);
                  setSelectedIds([]);
                  setSelectAll(false);
                }}
                className={`w-full text-left px-4 py-2 rounded-lg transition ${
                  selectedTopic === topic
                    ? "bg-blue-900/40 text-blue-300 border border-blue-500"
                    : "bg-[#1a202c] hover:bg-[#222a36]"
                }`}
              >
                {topic}
              </button>
            ))}
          </div>
        </aside>

        {/* MAIN PANEL */}
        <main className="flex-1 p-10">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-blue-400">
              Information Manager Dashboard
            </h1>

            <button
              onClick={deleteSelected}
              disabled={selectedIds.length === 0}
              className="px-4 py-2 bg-red-600 disabled:bg-red-900/40 disabled:opacity-40 text-white rounded-lg shadow hover:bg-red-700 transition"
            >
              Delete Selected ({selectedIds.length})
            </button>
          </div>

          <p className="text-gray-400 text-sm mb-4">
            Select multiple conversations using the checkboxes to delete them at once.
          </p>

          <h2 className="text-2xl font-semibold text-blue-300 mb-6">
            {selectedTopic}
          </h2>

          <div className="bg-[#11171f] rounded-2xl p-8 border border-[#1c2128]">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="text-gray-400 text-sm border-b border-gray-700">
                  <th className="py-3 w-12">
                    <input
                      type="checkbox"
                      className="premium-checkbox"
                      checked={selectAll}
                      onChange={(e) => {
                        e.stopPropagation();
                        toggleSelectAllRows();
                      }}
                    />
                  </th>
                  <th className="py-3">Conversation</th>
                  <th className="py-3">Stored</th>
                  <th className="py-3">Expires</th>
                  <th className="py-3">Actions</th>
                </tr>
              </thead>

              <tbody>
                {filtered.map((row) => (
                  <tr
                    key={row.id}
                    onClick={(e) => {
                      const target = e.target as HTMLElement;
                      if (target.closest("input") || target.closest("button")) return;
                      setModalEntry(row);
                    }}
                    className="border-b border-gray-800 hover:bg-[#1a202c] transition cursor-pointer"
                  >
                    <td className="py-3">
                      <input
                        type="checkbox"
                        className="premium-checkbox"
                        checked={selectedIds.includes(row.id)}
                        onChange={(e) => {
                          e.stopPropagation();
                          toggleSelect(row.id);
                        }}
                      />
                    </td>

                    <td className="py-3 text-gray-300 max-w-[400px] truncate">
                      {row.reformulated ?? row.sanitized ?? row.original}
                    </td>

                    <td className="py-3 text-gray-400">
                      {new Date(row.created_at).toLocaleString()}
                    </td>

                    <td className="py-3 text-gray-400">
                      {new Date(row.expires_at).toLocaleString()}
                    </td>

                    <td className="py-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteEntry(row.id);
                        }}
                        className="text-red-400 hover:text-red-300"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      </div>

      {/* MODAL */}
      {modalEntry && (
        <ConversationModal
          entry={modalEntry}
          onClose={() => setModalEntry(null)}
          onDelete={deleteEntry}
          onUpdateRetention={updateRetention}
        />
      )}
    </>
  );
}
