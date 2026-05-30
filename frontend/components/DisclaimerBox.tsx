import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTriangleExclamation, faChevronDown } from '@fortawesome/free-solid-svg-icons';

interface DisclaimerBoxProps {
  message?: string;
  disclaimer?: string;
  variant?: 'card' | 'banner';
  collapsible?: boolean;
}

const DEFAULT_MESSAGE =
  'MediScan AI is for educational and informational purposes only. ' +
  'It does not provide medical diagnosis, treatment, or professional medical advice. ' +
  'Always consult a licensed healthcare professional before making any health-related decisions.';

const DisclaimerBox: React.FC<DisclaimerBoxProps> = ({
  message,
  disclaimer,
  variant = 'card',
  collapsible = false,
}) => {
  const [expanded, setExpanded] = useState(true);
  const text = message || disclaimer || DEFAULT_MESSAGE;

  if (variant === 'banner') {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-2 text-xs text-amber-800 flex items-center gap-2">
        <FontAwesomeIcon icon={faTriangleExclamation} className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
        <span>{text}</span>
      </div>
    );
  }

  return (
    <div className="rounded-xl border-2 border-amber-200 bg-amber-50 overflow-hidden">
      <div
        className={`flex items-center gap-3 px-5 py-3.5 ${collapsible ? 'cursor-pointer select-none' : ''}`}
        onClick={collapsible ? () => setExpanded((v) => !v) : undefined}
        role={collapsible ? 'button' : undefined}
        aria-expanded={collapsible ? expanded : undefined}
      >
        <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: '#f59e0b' }}>
          <FontAwesomeIcon icon={faTriangleExclamation} className="w-3.5 h-3.5 text-white" />
        </div>
        <h3 className="font-bold text-amber-900 text-sm flex-1">Medical Disclaimer</h3>
        {collapsible && (
          <FontAwesomeIcon
            icon={faChevronDown}
            className={`w-4 h-4 text-amber-600 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}
          />
        )}
      </div>

      {(!collapsible || expanded) && (
        <div className="px-5 pb-4 pt-0">
          <p className="text-amber-800 text-sm leading-relaxed">{text}</p>
        </div>
      )}
    </div>
  );
};

export default DisclaimerBox;
