import { motion } from 'motion/react';
import { Github } from 'lucide-react';

export function Hero() {
  return (
    <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
      {/* Background glowing effects */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-900/20 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center">

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-left"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/50 border border-cyan-800/50 text-cyan-400 text-sm font-medium mb-6">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
              </span>
              v0.1 is now live
            </div>
            <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight text-neutral-100 mb-6 leading-[1.1]">
              Unmask the spy among your <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">friends.</span>
            </h1>
            <p className="text-lg text-neutral-400 mb-8 max-w-xl">
              Polygraph is a multiplayer party game bot for Telegram, inspired by classic hidden-role games. Instantly host a room, answer subtle questions, and vote to uncover who is deceiving the group.
            </p>
            <div className="flex flex-wrap items-center gap-4">
              <a
                href="https://github.com/PiterPentester/polygraph"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-neutral-950 font-semibold transition-colors shadow-[0_0_20px_rgba(34,211,238,0.3)] hover:shadow-[0_0_30px_rgba(34,211,238,0.5)]"
              >
                <Github className="w-5 h-5" />
                View Repository
              </a>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="rounded-xl overflow-hidden border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm shadow-[0_0_40px_rgba(34,211,238,0.15)] group relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <img
                src="https://raw.githubusercontent.com/PiterPentester/polygraph/main/assets/logo.jpg"
                alt="Polygraph Bot Logo"
                className="w-full h-auto object-cover transform transition-transform duration-700 group-hover:scale-105"
                referrerPolicy="no-referrer"
              />
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
