import React from 'react';
import { LabResult } from '@/lib/api';
import StatusBadge from './StatusBadge';

interface ResultsTableProps {
  results: LabResult[];
}

const ROW_HIGHLIGHT: Record<string, string> = {
  high:    'bg-red-50/60 hover:bg-red-50',
  low:     'bg-blue-50/60 hover:bg-blue-50',
  normal:  'hover:bg-green-50/40',
  unknown: 'hover:bg-gray-50/40',
};

const ResultsTable: React.FC<ResultsTableProps> = ({ results }) => {
  if (!results || results.length === 0) {
    return (
      <div className="py-14 flex flex-col items-center justify-center text-gray-400">
        <svg className="w-14 h-14 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="font-medium text-gray-500">No lab results found in this report.</p>
        <p className="text-sm mt-1">
          The OCR may not have detected structured lab data. Try a clearer image or PDF.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-100" role="table">
        <thead style={{ backgroundColor: '#DDE6ED' }}>
          <tr>
            {['Test Name', 'Value', 'Unit', 'Reference Range', 'Status'].map((h) => (
              <th
                key={h}
                scope="col"
                className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider"
                style={{ color: '#526D82' }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {results.map((result) => {
            const rowClass = ROW_HIGHLIGHT[result.status] || ROW_HIGHLIGHT.unknown;
            const refText =
              result.ref_text ||
              (result.ref_low !== null && result.ref_high !== null
                ? `${result.ref_low} – ${result.ref_high}`
                : result.ref_low !== null
                ? `> ${result.ref_low}`
                : result.ref_high !== null
                ? `< ${result.ref_high}`
                : '—');

            return (
              <tr key={result.id} className={`transition-colors ${rowClass}`}>
                <td className="px-6 py-4">
                  <div className="font-semibold text-gray-900 text-sm">
                    {result.canonical_name || result.test_name}
                  </div>
                  {result.canonical_name && result.canonical_name !== result.test_name && (
                    <div className="text-xs text-gray-400 mt-0.5">{result.test_name}</div>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className="font-bold text-gray-900 text-sm">
                    {result.value_text || (result.value_numeric !== null ? String(result.value_numeric) : '—')}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">
                  {result.unit || '—'}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">
                  {refText}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={result.status as any} size="sm" />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;
