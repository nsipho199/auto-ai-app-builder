import Calculator from "@/components/Calculator";

export const metadata = {
  title: "Calculator – Auto AI App Builder",
  description: "A simple calculator.",
};

export default function CalculatorPage() {
  return (
    <div className="flex flex-col items-center gap-6">
      <h2 className="text-xl font-semibold tracking-tight">Calculator</h2>
      <Calculator />
    </div>
  );
}
