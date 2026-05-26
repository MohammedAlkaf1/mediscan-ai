import React from 'react';
import { TrendDataPoint } from '@/lib/api';

interface TrendChartProps {
  dataPoints: TrendDataPoint[];
  testName: string;
  trend: string;
}

const STATUS_COLORS: Record<string, string> = {
  normal: '#22c55e',
  high: '#ef4444',
  low: '#3b82f6',
  unknown: '#9ca3af',
};

const TREND_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  increasing: { label: 'Increasing', color: '#f59e0b', icon: '↑' },
  decreasing: { label: 'Decreasing', color: '#3b82f6', icon: '↓' },
  stable: { label: 'Stable', color: '#22c55e', icon: '→' },
  insufficient_data: { label: 'Not enough data', color: '#9ca3af', icon: '…' },
};

const TrendChart: React.FC<TrendChartProps> = ({ dataPoints, testName, trend }) => {
  const numericPoints = dataPoints.filter(
    (dp) => typeof dp.value === 'number' && dp.value !== null
  ) as (TrendDataPoint & { value: number })[];

  const trendCfg = TREND_CONFIG[trend] || TREND_CONFIG.insufficient_data;

  if (numericPoints.length < 2) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
        Not enough data to display a chart
      </div>
    );
  }

  // SVG chart dimensions
  const W = 500;
  const H = 160;
  const PAD = { top: 16, right: 20, bottom: 32, left: 44 };
  const chartW = W - PAD.left - PAD.right;
  const chartH = H - PAD.top - PAD.bottom;

  const values = numericPoints.map((p) => p.value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const valRange = maxVal - minVal || 1;

  const xStep = chartW / (numericPoints.length - 1);

  const toX = (i: number) => PAD.left + i * xStep;
  const toY = (v: number) =>
    PAD.top + chartH - ((v - minVal) / valRange) * chartH;

  const pathD = numericPoints
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${toX(i).toFixed(1)} ${toY(p.value).toFixed(1)}`)
    .join(' ');

  // Y axis ticks
  const yTicks = 4;
  const yTickValues = Array.from({ length: yTicks + 1 }, (_, i) =>
    minVal + (valRange * i) / yTicks
  );

  const unit = numericPoints[0]?.unit || '';

  return (
    <div className="w-full overflow-x-auto">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        style={{ minWidth: '280px', maxWidth: '600px' }}
        aria-label={`Trend chart for ${testName}`}
      >
        {/* Grid lines */}
        {yTickValues.map((v, i) => {
          const y = toY(v);
          return (
            <g key={i}>
              <line
                x1={PAD.left}
                x2={W - PAD.right}
                y1={y}
                y2={y}
                stroke="#e5e7eb"
                strokeWidth={1}
              />
              <text
                x={PAD.left - 6}
                y={y + 4}
                textAnchor="end"
                fontSize={10}
                fill="#6b7280"
              >
                {v % 1 === 0 ? v.toFixed(0) : v.toFixed(1)}
              </text>
            </g>
          );
        })}

        {/* Line */}
        <path
          d={pathD}
          fill="none"
          stroke="#526D82"
          strokeWidth={2.5}
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* Area fill */}
        <path
          d={`${pathD} L ${toX(numericPoints.length - 1).toFixed(1)} ${H - PAD.bottom} L ${PAD.left} ${H - PAD.bottom} Z`}
          fill="url(#areaGradient)"
          opacity={0.2}
        />

        <defs>
          <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#526D82" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#526D82" stopOpacity={0} />
          </linearGradient>
        </defs>

        {/* Data points */}
        {numericPoints.map((p, i) => {
          const cx = toX(i);
          const cy = toY(p.value);
          const color = STATUS_COLORS[p.status] || '#9ca3af';
          return (
            <g key={i}>
              <circle cx={cx} cy={cy} r={5} fill="white" stroke={color} strokeWidth={2.5} />
              {/* X-axis date label */}
              {p.date && (
                <text
                  x={cx}
                  y={H - PAD.bottom + 14}
                  textAnchor="middle"
                  fontSize={9}
                  fill="#9ca3af"
                >
                  {new Date(p.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </text>
              )}
              {/* Value label above point */}
              <text
                x={cx}
                y={cy - 10}
                textAnchor="middle"
                fontSize={10}
                fontWeight="bold"
                fill={color}
              >
                {p.value}
              </text>
            </g>
          );
        })}

        {/* Y axis unit */}
        {unit && (
          <text
            x={PAD.left - 28}
            y={PAD.top + chartH / 2}
            textAnchor="middle"
            fontSize={9}
            fill="#6b7280"
            transform={`rotate(-90, ${PAD.left - 28}, ${PAD.top + chartH / 2})`}
          >
            {unit}
          </text>
        )}
      </svg>

      {/* Status legend */}
      <div className="flex items-center gap-4 mt-2 flex-wrap">
        {Object.entries(STATUS_COLORS).map(([status, color]) => (
          <span key={status} className="flex items-center gap-1 text-xs text-gray-500">
            <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: color }} />
            {status}
          </span>
        ))}
        <span
          className="ml-auto text-xs font-semibold px-2 py-0.5 rounded-full"
          style={{ background: trendCfg.color + '20', color: trendCfg.color }}
        >
          {trendCfg.icon} {trendCfg.label}
        </span>
      </div>
    </div>
  );
};

export default TrendChart;
