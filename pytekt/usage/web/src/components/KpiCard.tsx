import { motion } from "framer-motion";

interface Props {
  label: string;
  value: string;
  hint?: string;
  accent?: boolean;
  small?: boolean;
  delay?: number;
  className?: string;
}

export function KpiCard({
  label,
  value,
  hint,
  accent,
  small,
  delay = 0,
  className = "span-3",
}: Props) {
  return (
    <motion.div
      className={`card ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="kpi-label">{label}</div>
      <motion.div
        className={`kpi-value ${accent ? "accent" : ""} ${small ? "small" : ""}`}
        key={value}
        initial={{ opacity: 0, scale: 0.92 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.35 }}
      >
        {value}
      </motion.div>
      {hint && <div className="kpi-hint">{hint}</div>}
    </motion.div>
  );
}
