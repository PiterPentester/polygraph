import { Github, Fingerprint } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-neutral-950 border-t border-neutral-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2">
          <Fingerprint className="w-6 h-6 text-cyan-400" />
          <span className="text-lg font-bold tracking-tight text-neutral-200">Polygraph</span>
        </div>
        
        <p className="text-sm text-neutral-500 text-center md:text-left">
          Created and maintained by <a href="https://github.com/PiterPentester" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline">PiterPentester</a>. Open source under the MIT License.
        </p>
        
        <div className="flex items-center gap-4">
          <a href="https://github.com/PiterPentester/polygraph" target="_blank" rel="noopener noreferrer" className="text-neutral-500 hover:text-neutral-300 transition-colors">
            <span className="sr-only">GitHub</span>
            <Github className="w-5 h-5" />
          </a>
        </div>
      </div>
    </footer>
  );
}
