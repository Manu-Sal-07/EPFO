import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'PF Compass | Citizen-First EPFO Portal',
  description: 'A transparent, citizen-first redesign of the Employees Provident Fund experience.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
