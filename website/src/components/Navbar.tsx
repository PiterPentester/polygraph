import { Github, Fingerprint } from 'lucide-react';

export function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 bg-neutral-950/80 backdrop-blur-md border-b border-neutral-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <Fingerprint className="w-8 h-8 text-cyan-400" />
            <span className="text-xl font-bold tracking-tight text-neutral-100">Polygraph</span>
          </div>
          <div className="flex items-center gap-4">
            <a 
              href="https://github.com/PiterPentester/polygraph"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm font-medium text-neutral-300 hover:text-cyan-400 transition-colors"
            >
              <Github className="w-5 h-5" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
