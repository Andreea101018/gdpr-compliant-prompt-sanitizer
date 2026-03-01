"use client";

import React, { useState } from "react";
import TopNav from "@/components/TopNav";

function PopupMessage({ message, onClose }: { message: string; onClose: () => void }) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
      <div className="bg-[#111827] text-gray-200 p-6 rounded-2xl shadow-2xl shadow-black/40 w-[360px] text-center border border-gray-700">
        <p className="font-semibold text-lg mb-4">{message}</p>
        <button
          onClick={onClose}
          className="px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-500 transition-all duration-200 hover:scale-[1.03] shadow-md shadow-blue-600/20"
        >
          OK
        </button>
      </div>
    </div>
  );
}

function ApprovalPopup({
  reformulated,
  setReformulated,
  onApprove,
  onCancel,
}: {
  reformulated: string;
  setReformulated: (value: string) => void;
  onApprove: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
      <div className="bg-[#1f2937] p-6 rounded-2xl w-[520px] shadow-2xl shadow-black/40 border border-gray-700">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">
          Approve Reformulated Prompt
        </h2>

        <textarea
          className="w-full min-h-[140px] bg-[#0f172a] border border-gray-700 rounded-xl p-3 text-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/40 transition"
          value={reformulated}
          onChange={(e) => setReformulated(e.target.value)}
        />

        <div className="flex justify-end gap-4 mt-6">
          <button
            className="px-4 py-2 bg-gray-700 rounded-lg text-gray-200 hover:bg-gray-600 transition"
            onClick={onCancel}
          >
            Cancel
          </button>

          <button
            className="px-4 py-2 bg-green-600 rounded-lg text-white hover:bg-green-500 transition shadow-md shadow-green-600/20"
            onClick={onApprove}
          >
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}

export default function GDPRFirewall() {
  const [input, setInput] = useState("");
  const [original, setOriginal] = useState("");
  const [topic, setTopic] = useState("");
  const [detected, setDetected] = useState<any[]>([]);
  const [choices, setChoices] = useState<Record<string, string>>({});
  const [finalSanitized, setFinalSanitized] = useState<string | null>(null);
  const [reformulated, setReformulated] = useState<string | null>(null);
  const [showApprovalPopup, setShowApprovalPopup] = useState(false);
  const [loading, setLoading] = useState(false);

  const [retention, setRetention] = useState("30d");
  const [customDays, setCustomDays] = useState("");
  const [retentionError, setRetentionError] = useState<string | null>(null);

  const [popup, setPopup] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function validateCustomDays(value: string) {
    if (!value) {
      setRetentionError("Please enter a number between 1 and 365.");
      return false;
    }
    const num = Number(value);
    if (num < 1 || num > 365) {
      setRetentionError("Retention must be between 1 and 365 days.");
      return false;
    }
    setRetentionError(null);
    return true;
  }

  function getRetentionValue() {
    if (retention === "custom") return `${customDays}d`;
    return retention;
  }

  async function handleSanitize() {
    if (input.trim().length === 0) {
      setError("Please type a message before sanitizing.");
      return;
    }

    setLoading(true);
    setDetected([]);
    setFinalSanitized(null);
    setReformulated(null);

    const res = await fetch("http://localhost:5000/api/sanitize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: input }),
    });

    const json = await res.json();

    setOriginal(json.original);
    setTopic(json.topic);
    setDetected(json.detected);

    const initialChoices: Record<string, string> = {};
    json.detected.forEach((item: any) => (initialChoices[item.id] = "remove"));

    setChoices(initialChoices);
    setLoading(false);
  }

  async function sanitizeMessage() {
    const res = await fetch("http://localhost:5000/api/apply_mask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: original, detected, choices }),
    });

    const json = await res.json();
    setFinalSanitized(json.final_text);
  }

  async function reformulatePrompt() {
    if (!finalSanitized) {
      setError("Please sanitize first.");
      return;
    }

    const kept = detected.filter((i) => choices[i.id] === "keep");

    const res = await fetch("http://localhost:5000/api/reformulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sanitized: finalSanitized, kept_items: kept }),
    });

    const json = await res.json();
    setReformulated(json.reformulated);
    setShowApprovalPopup(true);
  }

  async function saveReformulated() {
    if (!reformulated) return;
    const retentionValue = getRetentionValue();

    await fetch("http://localhost:5000/api/save_reformulated", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reformulated, topic, retention: retentionValue }),
    });

    setPopup("Reformulated prompt saved.");
  }

  async function saveSanitizedVersion() {
    if (!finalSanitized) return;
    const retentionValue = getRetentionValue();

    await fetch("http://localhost:5000/api/save_sanitized", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sanitized: finalSanitized, topic, retention: retentionValue }),
    });

    setPopup("Sanitized message saved.");
  }

  async function saveOriginalMessage() {
    const retentionValue = getRetentionValue();

    await fetch("http://localhost:5000/api/save_original", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ original, topic, retention: retentionValue }),
    });

    setPopup("Original message saved.");
  }

  function approvePrompt() {
    setShowApprovalPopup(false);
    setPopup("Prompt approved.");
  }

  return (
    <>
      <TopNav />

      <div className="min-h-screen bg-[#0d1117] text-gray-200 px-8 py-10">

        <div className="max-w-4xl mx-auto text-center mb-14 animate-fadeIn">
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-100 to-blue-300">
            GDPR Privacy Firewall
          </h1>
          <p className="text-gray-400 text-lg mt-2">
            Sanitize sensitive user data before sharing it with AI
          </p>
        </div>

        <div className="bg-[#111827] p-10 rounded-3xl border border-gray-800 shadow-2xl shadow-black/30 backdrop-blur-sm max-w-4xl mx-auto transition-all duration-200">
          <textarea
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              if (error) setError(null);
            }}
            placeholder="Write something that may contain sensitive data…"
            className="w-full min-h-[160px] bg-[#0f172a] border border-gray-700 rounded-2xl p-4 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/40 transition shadow-inner"
          />

          {error && <p className="text-red-400 mt-3">{error}</p>}

          <button
            onClick={handleSanitize}
            disabled={loading}
            className="mt-5 px-6 py-2 bg-blue-600 rounded-xl text-white shadow-md shadow-blue-600/20 hover:bg-blue-500 transition-all duration-200 hover:scale-[1.03] disabled:opacity-50"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                Analyzing…
              </div>
            ) : (
              "Analyze Message"
            )}
          </button>
        </div>

        {original && (
          <div className="bg-[#111827] p-10 rounded-3xl border border-gray-800 shadow-2xl shadow-black/30 backdrop-blur-sm max-w-4xl mx-auto mt-12 animate-fadeIn">

            <div className="mb-6">
              <h3 className="text-sm text-gray-400 font-medium">Detected Topic</h3>
              <span className="inline-block bg-blue-900/30 text-blue-300 px-4 py-1 rounded-full text-sm border border-blue-800 mt-2">
                {topic}
              </span>
            </div>

            <div>
              <h3 className="text-sm text-gray-400 mb-1">Original Message</h3>
              <div className="bg-[#0f172a] border border-gray-700 rounded-xl p-4">
                {original}
              </div>
            </div>

            <div className="mt-10">
              <h3 className="text-sm text-red-400 font-medium mb-3">Detected Sensitive Data</h3>

              <div className="space-y-4">
                {detected.map((item) => (
                  <div
                    key={item.id}
                    className="flex justify-between items-center bg-red-900/20 border border-red-700/40 p-4 rounded-xl hover:bg-red-900/30 transition-all duration-150 backdrop-blur-sm"
                  >
                    <div>
                      <p className="font-semibold text-red-300">{item.type}</p>
                      <p className="text-gray-300">{item.text}</p>
                    </div>

                    <div className="flex gap-3">
                      <button
                        className={`px-3 py-1 text-sm rounded-lg transition ${
                          choices[item.id] === "keep"
                            ? "bg-green-600 text-white shadow shadow-green-600/30"
                            : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                        }`}
                        onClick={() => setChoices({ ...choices, [item.id]: "keep" })}
                      >
                        KEEP
                      </button>

                      <button
                        className={`px-3 py-1 text-sm rounded-lg transition ${
                          choices[item.id] === "remove"
                            ? "bg-red-600 text-white shadow shadow-red-600/30"
                            : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                        }`}
                        onClick={() => setChoices({ ...choices, [item.id]: "remove" })}
                      >
                        REMOVE
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={sanitizeMessage}
              className="mt-8 px-6 py-2 rounded-xl bg-green-600 text-white hover:bg-green-500 transition-all duration-200 hover:scale-[1.03] shadow-md shadow-green-600/20"
            >
              Sanitize Message
            </button>

            {finalSanitized && (
              <>
                <div className="mt-12">
                  <h3 className="text-sm text-green-400 font-medium">Sanitized Output</h3>
                  <div className="bg-[#0f172a] border border-gray-700 rounded-xl p-4 mt-2">
                    {finalSanitized}
                  </div>
                </div>

                <button
                  onClick={reformulatePrompt}
                  className="mt-6 px-6 py-2 rounded-xl bg-blue-600 text-white hover:bg-blue-500 transition-all duration-200 shadow-md shadow-blue-600/20 hover:scale-[1.03]"
                >
                  Reformulate Prompt
                </button>
              </>
            )}

            {reformulated && (
              <div className="mt-10">
                <h3 className="text-sm text-yellow-400 font-medium">Reformulated Prompt</h3>
                <div className="bg-[#0f172a] border border-gray-700 rounded-xl p-4 mt-2">
                  {reformulated}
                </div>
              </div>
            )}

            {finalSanitized && (
              <div className="mt-10 bg-[#0f172a] border border-gray-700 rounded-2xl p-6 shadow-inner backdrop-blur-sm">
                <h3 className="text-gray-300 font-medium mb-4">Retention Period</h3>

                <div className="flex items-center gap-4">
                  <span className="text-gray-400 w-28">Preset</span>

                  <select
                    value={retention}
                    onChange={(e) => {
                      setRetention(e.target.value);
                      if (e.target.value !== "custom") {
                        setCustomDays("");
                        setRetentionError(null);
                      }
                    }}
                    className="px-3 py-2 bg-[#111827] border border-gray-700 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-500/40 transition"
                  >
                    <option value="7d">7 days</option>
                    <option value="30d">30 days</option>
                    <option value="90d">90 days</option>
                    <option value="365d">1 year</option>
                    <option value="custom">Custom…</option>
                  </select>
                </div>

                {retention === "custom" && (
                  <div className="flex items-center gap-4 mt-4">
                    <span className="text-gray-400 w-28">Custom</span>

                    <input
                      type="number"
                      min={1}
                      max={365}
                      value={customDays}
                      onChange={(e) => {
                        let val = Number(e.target.value);
                        if (val < 1) val = 1;
                        if (val > 365) val = 365;
                        setCustomDays(String(val));
                        validateCustomDays(String(val));
                      }}
                      placeholder="Days"
                      className="px-3 py-2 w-28 bg-[#111827] border border-gray-700 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-500/40 transition"
                    />

                    {retentionError && (
                      <p className="text-red-400 text-xs">{retentionError}</p>
                    )}
                  </div>
                )}
              </div>
            )}

            {finalSanitized && (
              <div className="mt-10 flex flex-wrap gap-4">
                <button
                  onClick={saveReformulated}
                  disabled={!reformulated}
                  className="px-4 py-2 rounded-xl text-sm bg-yellow-600 hover:bg-yellow-500 text-white shadow-md shadow-yellow-600/20 transition disabled:opacity-50"
                >
                  Save Reformulated Prompt
                </button>

                <button
                  onClick={saveSanitizedVersion}
                  className="px-4 py-2 rounded-xl text-sm bg-green-600 hover:bg-green-500 text-white shadow-md shadow-green-600/20 transition"
                >
                  Save Sanitized Version
                </button>

                <button
                  onClick={saveOriginalMessage}
                  className="px-4 py-2 rounded-xl text-sm bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20 transition"
                >
                  Save Original Message
                </button>
              </div>
            )}
          </div>
        )}

        {popup && <PopupMessage message={popup} onClose={() => setPopup(null)} />}

        {showApprovalPopup && reformulated && (
          <ApprovalPopup
            reformulated={reformulated}
            setReformulated={setReformulated}
            onApprove={approvePrompt}
            onCancel={() => setShowApprovalPopup(false)}
          />
        )}
      </div>
    </>
  );
}
