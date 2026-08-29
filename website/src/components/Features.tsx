import { motion } from 'motion/react';
import { Link, FileText, RefreshCcw, Users, Zap, Server } from 'lucide-react';

const features = [
  {
    name: 'Deep-Link Room Creation',
    description: 'Instant one-click joins via Telegram deep-links. No need for players to type room codes—just click and play.',
    icon: Link,
  },
  {
    name: 'Dynamic CSV Question Pool',
    description: 'Easily expand the game by dropping .csv files into the assets folder. Polygraph automatically detects and loads new questions.',
    icon: FileText,
  },
  {
    name: 'No Repeated Questions',
    description: 'Session-level tracking guarantees questions do not repeat during a room\'s active session, keeping the game fresh.',
    icon: RefreshCcw,
  },
  {
    name: 'Host Management',
    description: 'Take full control of the lobby. Configure the number of spies, kick inactive players, and instantly trigger rematches.',
    icon: Users,
  },
  {
    name: 'Asynchronous & Fast',
    description: 'Powered by Python 3.12 and aiogram 3.x, ensuring the bot remains snappy and responsive even with many active rooms.',
    icon: Zap,
  },
  {
    name: 'Docker & Kubernetes Ready',
    description: 'Deploy anywhere with ease. Includes lightweight multi-stage container builds and production-ready k8s manifests.',
    icon: Server,
  },
];

export function Features() {
  return (
    <section className="py-24 bg-neutral-950 relative border-t border-neutral-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl font-bold tracking-tight text-neutral-100 sm:text-4xl mb-4">
            Built for Seamless Gameplay
          </h2>
          <p className="text-lg text-neutral-400">
            Polygraph handles all the heavy lifting of state management and question distribution, so you can focus on finding the spy.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-neutral-900/50 border border-neutral-800 rounded-2xl p-8 hover:bg-neutral-900 hover:border-neutral-700 transition-colors"
            >
              <div className="w-12 h-12 rounded-lg bg-cyan-950/50 border border-cyan-800 flex items-center justify-center mb-6 text-cyan-400">
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-neutral-200 mb-3">
                {feature.name}
              </h3>
              <p className="text-neutral-400 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
