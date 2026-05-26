import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faClock,
  faGear,
  faCheck,
  faXmark,
  faArrowUp,
  faArrowDown,
  faQuestion,
} from '@fortawesome/free-solid-svg-icons';
import { IconDefinition } from '@fortawesome/fontawesome-svg-core';

interface StatusBadgeProps {
  status: 'queued' | 'processing' | 'done' | 'failed' | 'normal' | 'high' | 'low' | 'unknown';
  size?: 'sm' | 'md' | 'lg';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const sizeClasses = {
    sm: 'text-xs px-2.5 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  const statusConfig: Record<string, { color: string; label: string; icon: IconDefinition }> = {
    queued:     { color: 'bg-gray-100 text-gray-700 border-gray-300',   label: 'Queued',      icon: faClock    },
    processing: { color: 'bg-blue-100 text-blue-700 border-blue-300',   label: 'Processing',  icon: faGear     },
    done:       { color: 'bg-green-100 text-green-700 border-green-300', label: 'Complete',   icon: faCheck    },
    failed:     { color: 'bg-red-100 text-red-700 border-red-300',       label: 'Failed',     icon: faXmark    },
    normal:     { color: 'bg-green-100 text-green-700 border-green-300', label: 'Normal',     icon: faCheck    },
    high:       { color: 'bg-red-100 text-red-700 border-red-300',       label: 'High',       icon: faArrowUp  },
    low:        { color: 'bg-yellow-100 text-yellow-700 border-yellow-300', label: 'Low',     icon: faArrowDown},
    unknown:    { color: 'bg-gray-100 text-gray-600 border-gray-300',    label: 'Unknown',    icon: faQuestion },
  };

  const config = statusConfig[status] || statusConfig.unknown;

  return (
    <span className={`inline-flex items-center gap-1.5 font-semibold rounded-lg border ${config.color} ${sizeClasses[size]} shadow-sm`}>
      <FontAwesomeIcon icon={config.icon} className="w-3 h-3" />
      {config.label}
    </span>
  );
};

export default StatusBadge;
