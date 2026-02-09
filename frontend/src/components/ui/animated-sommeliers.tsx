"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { useCallback, useEffect, useState } from "react";
import { cn } from "@/lib/utils";

type Sommelier = {
  quote: string;
  name: string;
  role: string;
  focus: string;
  src: string;
  color: string;
  imagePosition?: string;
};

export const AnimatedSommeliers = ({
  sommeliers,
  autoplay = true,
  className,
}: {
  sommeliers: Sommelier[];
  autoplay?: boolean;
  className?: string;
}) => {
  const [active, setActive] = useState(0);

  const handleNext = useCallback(() => {
    if (sommeliers.length === 0) return;
    setActive((prev) => (prev + 1) % sommeliers.length);
  }, [sommeliers.length]);

  const handlePrev = useCallback(() => {
    if (sommeliers.length === 0) return;
    setActive((prev) => (prev - 1 + sommeliers.length) % sommeliers.length);
  }, [sommeliers.length]);

  const isActive = (index: number) => {
    return index === active;
  };

  useEffect(() => {
    if (autoplay) {
      const interval = setInterval(handleNext, 4000);
      return () => clearInterval(interval);
    }
  }, [autoplay, handleNext]);

  // Deterministic rotation based on index to avoid hydration mismatch
  const getRotation = (index: number) => {
    const rotations = [-8, 5, -3, 7, -6, 4, -9, 8, -2, 6];
    return rotations[index % rotations.length];
  };

  return (
    <div className={cn("max-w-sm md:max-w-5xl mx-auto px-4 md:px-8 lg:px-12 py-12", className)}>
      <div className="relative grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-20">
        {/* Image Stack */}
        <div>
          <div className="relative h-80 w-full">
            <AnimatePresence>
              {sommeliers.map((sommelier, index) => (
                <motion.div
                  key={sommelier.src}
                  initial={{
                    opacity: 0,
                    scale: 0.9,
                    z: -100,
                    rotate: getRotation(index),
                  }}
                  animate={{
                    opacity: isActive(index) ? 1 : 0.7,
                    scale: isActive(index) ? 1 : 0.95,
                    z: isActive(index) ? 0 : -100,
                    rotate: isActive(index) ? 0 : getRotation(index),
                    zIndex: isActive(index)
                      ? 999
                      : sommeliers.length + 2 - index,
                    y: isActive(index) ? [0, -40, 0] : 0,
                  }}
                  exit={{
                    opacity: 0,
                    scale: 0.9,
                    z: 100,
                    rotate: getRotation(index),
                  }}
                  transition={{
                    duration: 0.4,
                    ease: "easeInOut",
                  }}
                  className="absolute inset-0 origin-bottom"
                >
                  <div 
                    className="h-full w-full rounded-3xl overflow-hidden shadow-lg"
                    style={{ 
                      background: `linear-gradient(180deg, ${sommelier.color} 0%, ${sommelier.color}dd 100%)` 
                    }}
                  >
                    <Image
                      src={sommelier.src}
                      alt={sommelier.name}
                      width={500}
                      height={500}
                      draggable={false}
                      className="h-full w-full object-cover"
                      style={{ objectPosition: sommelier.imagePosition || 'top' }}
                    />
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

        {/* Content */}
        <div className="flex justify-between flex-col py-4">
          <motion.div
            key={active}
            initial={{
              y: 20,
              opacity: 0,
            }}
            animate={{
              y: 0,
              opacity: 1,
            }}
            exit={{
              y: -20,
              opacity: 0,
            }}
            transition={{
              duration: 0.2,
              ease: "easeInOut",
            }}
          >
            <div 
              className="inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-4"
              style={{ backgroundColor: sommeliers[active].color }}
            >
              {sommeliers[active].focus}
            </div>
            <h3 className="text-3xl font-bold text-[#722F37]">
              {sommeliers[active].name}
            </h3>
            <p className="text-sm font-medium mt-1" style={{ color: sommeliers[active].color }}>
              {sommeliers[active].role}
            </p>
            <motion.p className="text-lg text-gray-600 mt-6 leading-relaxed">
              {sommeliers[active].quote.split(" ").map((word, index) => (
                <motion.span
                  key={index}
                  initial={{
                    filter: "blur(10px)",
                    opacity: 0,
                    y: 5,
                  }}
                  animate={{
                    filter: "blur(0px)",
                    opacity: 1,
                    y: 0,
                  }}
                  transition={{
                    duration: 0.2,
                    ease: "easeInOut",
                    delay: 0.02 * index,
                  }}
                  className="inline-block"
                >
                  {word}&nbsp;
                </motion.span>
              ))}
            </motion.p>
          </motion.div>

          {/* Navigation */}
          <div className="flex items-center gap-4 pt-8 md:pt-0">
            <button
              onClick={handlePrev}
              className="h-10 w-10 rounded-full bg-[#722F37]/10 flex items-center justify-center group/button hover:bg-[#722F37] transition-colors"
            >
              <ChevronLeft className="h-5 w-5 text-[#722F37] group-hover/button:text-white group-hover/button:-translate-x-0.5 transition-all" />
            </button>
            <div className="flex gap-2">
              {sommeliers.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setActive(index)}
                  className={cn(
                    "h-2 rounded-full transition-all",
                    isActive(index) 
                      ? "w-8 bg-[#722F37]" 
                      : "w-2 bg-[#722F37]/20 hover:bg-[#722F37]/40"
                  )}
                />
              ))}
            </div>
            <button
              onClick={handleNext}
              className="h-10 w-10 rounded-full bg-[#722F37]/10 flex items-center justify-center group/button hover:bg-[#722F37] transition-colors"
            >
              <ChevronRight className="h-5 w-5 text-[#722F37] group-hover/button:text-white group-hover/button:translate-x-0.5 transition-all" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
