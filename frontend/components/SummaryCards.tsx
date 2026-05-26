import React from 'react';
import { LabResult } from '@/lib/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck, faArrowUp, faArrowDown, faQuestion } from '@fortawesome/free-solid-svg-icons';

interface SummaryCardsProps {
  results: LabResult[];
}

const SummaryCards: React.FC<SummaryCardsProps> = ({ results }) => {
  const counts = results.reduce(
    (acc, result) => {
      acc[result.status] = (acc[result.status] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const cards = [
    {
      label: 'Normal',
      count: counts.normal || 0,
      dotColor: '#16a34a',
      bgColor: '#f0fdf4',
      textColor: '#16a34a',
      iconBg: '#16a34a',
      icon: faCheck,
    },
    {
      label: 'High',
      count: counts.high || 0,
      dotColor: '#dc2626',
      bgColor: '#fef2f2',
      textColor: '#dc2626',
      iconBg: '#dc2626',
      icon: faArrowUp,
    },
    {
      label: 'Low',
      count: counts.low || 0,
      dotColor: '#d97706',
      bgColor: '#fffbeb',
      textColor: '#d97706',
      iconBg: '#d97706',
      icon: faArrowDown,
    },
    {
      label: 'Unknown',
      count: counts.unknown || 0,
      dotColor: '#9DB2BF',
      bgColor: '#DDE6ED',
      textColor: '#526D82',
      iconBg: '#9DB2BF',
      icon: faQuestion,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-xl p-6 shadow-sm"
          style={{ backgroundColor: card.bgColor, border: `2px solid ${card.dotColor}30` }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: '#526D82' }}>{card.label}</p>
              <p className="text-3xl font-bold mt-2" style={{ color: card.textColor }}>
                {card.count}
              </p>
            </div>
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ backgroundColor: card.iconBg }}
            >
              <FontAwesomeIcon icon={card.icon} className="w-5 h-5 text-white" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SummaryCards;
