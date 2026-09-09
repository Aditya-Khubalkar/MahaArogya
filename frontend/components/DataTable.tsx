"use client";

import { ReactNode } from "react";

interface DataTableProps<T> {
  columns: {
    key: keyof T | string;
    header: string;
    render?: (item: T) => ReactNode;
  }[];
  data: T[];
  emptyMessage?: string;
}

export default function DataTable<T>({ columns, data, emptyMessage = "No data available." }: DataTableProps<T>) {
  return (
    <div className="table-container">
      {data.length === 0 ? (
        <div className="empty-state">{emptyMessage}</div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col, i) => (
                <th key={String(col.key) + i}>{col.header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item, i) => (
              <tr key={i}>
                {columns.map((col, j) => (
                  <td key={String(col.key) + j}>
                    {col.render ? col.render(item) : (item as any)[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <style jsx>{`
        .table-container {
          background: var(--surface-light);
          border: 1px solid var(--surface-border);
          border-radius: var(--radius-lg);
          overflow: hidden;
        }
        
        .empty-state {
          padding: 32px;
          text-align: center;
          color: var(--text-muted);
        }

        .data-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.9rem;
        }

        .data-table th,
        .data-table td {
          padding: 12px 16px;
          text-align: left;
        }

        .data-table th {
          background: rgba(0, 0, 0, 0.2);
          color: var(--text-secondary);
          font-weight: 500;
          font-size: 0.8rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          border-bottom: 1px solid var(--surface-border);
        }

        .data-table tr {
          border-bottom: 1px solid var(--surface-border);
          transition: background-color var(--transition-fast);
        }

        .data-table tr:last-child {
          border-bottom: none;
        }

        .data-table tr:hover {
          background: rgba(255, 255, 255, 0.02);
        }
      `}</style>
    </div>
  );
}
