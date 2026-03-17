import type { ReactNode } from "react";

interface AppShellProps {
  label: string;
  children: ReactNode;
}

export function AppShell({ label, children }: AppShellProps) {
  return (
    <main aria-label={label}>
      {children}
    </main>
  );
}
