"use client";

import { useState, useCallback } from "react";

type Operator = "+" | "-" | "×" | "÷";

export default function Calculator() {
  const [display, setDisplay] = useState("0");
  const [firstOperand, setFirstOperand] = useState<number | null>(null);
  const [operator, setOperator] = useState<Operator | null>(null);
  const [waitingForSecond, setWaitingForSecond] = useState(false);

  const inputDigit = useCallback(
    (digit: string) => {
      if (waitingForSecond) {
        setDisplay(digit);
        setWaitingForSecond(false);
      } else {
        setDisplay(display === "0" ? digit : display + digit);
      }
    },
    [display, waitingForSecond],
  );

  const inputDecimal = useCallback(() => {
    if (waitingForSecond) {
      setDisplay("0.");
      setWaitingForSecond(false);
      return;
    }
    if (!display.includes(".")) {
      setDisplay(display + ".");
    }
  }, [display, waitingForSecond]);

  const handleOperator = useCallback(
    (next: Operator) => {
      const current = parseFloat(display);

      if (firstOperand === null) {
        setFirstOperand(current);
      } else if (operator && !waitingForSecond) {
        const result = calculate(firstOperand, current, operator);
        setDisplay(formatResult(result));
        setFirstOperand(result);
      }

      setOperator(next);
      setWaitingForSecond(true);
    },
    [display, firstOperand, operator, waitingForSecond],
  );

  const handleEquals = useCallback(() => {
    if (firstOperand === null || operator === null) return;

    const current = parseFloat(display);
    const result = calculate(firstOperand, current, operator);
    setDisplay(formatResult(result));
    setFirstOperand(null);
    setOperator(null);
    setWaitingForSecond(true);
  }, [display, firstOperand, operator]);

  const clear = useCallback(() => {
    setDisplay("0");
    setFirstOperand(null);
    setOperator(null);
    setWaitingForSecond(false);
  }, []);

  const toggleSign = useCallback(() => {
    setDisplay(formatResult(parseFloat(display) * -1));
  }, [display]);

  const percentage = useCallback(() => {
    setDisplay(formatResult(parseFloat(display) / 100));
  }, [display]);

  const btn =
    "flex items-center justify-center rounded-xl text-lg font-medium transition-colors active:scale-95 select-none";
  const digitBtn = `${btn} bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600`;
  const opBtn = `${btn} bg-amber-500 text-white hover:bg-amber-400`;
  const fnBtn = `${btn} bg-slate-300 dark:bg-slate-600 hover:bg-slate-400 dark:hover:bg-slate-500`;

  return (
    <div className="mx-auto w-full max-w-xs">
      <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4 shadow-lg">
        {/* Display */}
        <div className="mb-4 flex items-end justify-end rounded-xl bg-slate-100 dark:bg-slate-900 px-4 py-3 min-h-[3.5rem]">
          <span className="text-3xl font-light tracking-tight truncate">
            {display}
          </span>
        </div>

        {/* Buttons */}
        <div className="grid grid-cols-4 gap-2">
          <button className={fnBtn} onClick={clear}>AC</button>
          <button className={fnBtn} onClick={toggleSign}>+/−</button>
          <button className={fnBtn} onClick={percentage}>%</button>
          <button className={`${opBtn} ${operator === "÷" && waitingForSecond ? "ring-2 ring-white" : ""}`} onClick={() => handleOperator("÷")}>÷</button>

          <button className={digitBtn} onClick={() => inputDigit("7")}>7</button>
          <button className={digitBtn} onClick={() => inputDigit("8")}>8</button>
          <button className={digitBtn} onClick={() => inputDigit("9")}>9</button>
          <button className={`${opBtn} ${operator === "×" && waitingForSecond ? "ring-2 ring-white" : ""}`} onClick={() => handleOperator("×")}>×</button>

          <button className={digitBtn} onClick={() => inputDigit("4")}>4</button>
          <button className={digitBtn} onClick={() => inputDigit("5")}>5</button>
          <button className={digitBtn} onClick={() => inputDigit("6")}>6</button>
          <button className={`${opBtn} ${operator === "-" && waitingForSecond ? "ring-2 ring-white" : ""}`} onClick={() => handleOperator("-")}>−</button>

          <button className={digitBtn} onClick={() => inputDigit("1")}>1</button>
          <button className={digitBtn} onClick={() => inputDigit("2")}>2</button>
          <button className={digitBtn} onClick={() => inputDigit("3")}>3</button>
          <button className={`${opBtn} ${operator === "+" && waitingForSecond ? "ring-2 ring-white" : ""}`} onClick={() => handleOperator("+")}>+</button>

          <button className={`${digitBtn} col-span-2`} onClick={() => inputDigit("0")}>0</button>
          <button className={digitBtn} onClick={inputDecimal}>.</button>
          <button className={`${btn} bg-amber-600 text-white hover:bg-amber-500`} onClick={handleEquals}>=</button>
        </div>
      </div>
    </div>
  );
}

function calculate(a: number, b: number, op: Operator): number {
  switch (op) {
    case "+": return a + b;
    case "-": return a - b;
    case "×": return a * b;
    case "÷": return b !== 0 ? a / b : 0;
  }
}

function formatResult(n: number): string {
  if (!Number.isFinite(n)) return "Error";
  const s = parseFloat(n.toPrecision(12)).toString();
  return s.length > 12 ? n.toExponential(6) : s;
}
