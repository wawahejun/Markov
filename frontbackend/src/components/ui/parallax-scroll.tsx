"use client";
import { useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "../../lib/utils";

interface ParallaxScrollSecondProps {
  images: string[];
  imageData?: any[];
  onImageClick?: (data: any, index: number) => void;
  className?: string;
}

export const ParallaxScrollSecond = ({
  images,
  imageData = [],
  onImageClick,
  className,
}: ParallaxScrollSecondProps) => {
  const gridRef = useRef<any>(null);
  const { scrollYProgress } = useScroll({
    container: gridRef,
    offset: ["start start", "end start"],
  });

  const translateYFirst = useTransform(scrollYProgress, [0, 1], [0, -200]);
  const translateXFirst = useTransform(scrollYProgress, [0, 1], [0, -200]);
  const rotateXFirst = useTransform(scrollYProgress, [0, 1], [0, -20]);

  const translateYThird = useTransform(scrollYProgress, [0, 1], [0, -200]);
  const translateXThird = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const rotateXThird = useTransform(scrollYProgress, [0, 1], [0, 20]);

  const third = Math.ceil(images.length / 3);

  const firstPart = images.slice(0, third);
  const secondPart = images.slice(third, 2 * third);
  const thirdPart = images.slice(2 * third);

  const getDataForIndex = (partIndex: number, partType: 'first' | 'second' | 'third') => {
    let index: number;
    if (partType === 'first') {
      index = partIndex;
    } else if (partType === 'second') {
      index = third + partIndex;
    } else {
      index = 2 * third + partIndex;
    }
    return imageData[index] || null;
  };

  return (
    <div
      className={cn("h-[40rem] items-start overflow-y-auto w-full", className)}
      ref={gridRef}
    >
      <div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 items-start max-w-5xl mx-auto gap-10 py-40 px-10"
      >
        <div className="grid gap-10">
          {firstPart.map((el, idx) => {
            const data = getDataForIndex(idx, 'first');
            return (
              <motion.div
                style={{
                  y: translateYFirst,
                  x: translateXFirst,
                  rotateZ: rotateXFirst,
                }}
                key={`grid-1-${idx}`}
                onClick={() => onImageClick && data && onImageClick(data, idx)}
                className="cursor-pointer hover:scale-105 transition-transform duration-300"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                <div className="overflow-hidden rounded-xl shadow-xl">
                  <img
                    src={el}
                    className="h-80 w-full object-cover object-left-top rounded-lg transition-transform duration-300 hover:scale-110"
                    alt="thumbnail"
                  />
                </div>
              </motion.div>
            );
          })}
        </div>
        <div className="grid gap-10">
          {secondPart.map((el, idx) => {
            const data = getDataForIndex(idx, 'second');
            return (
              <motion.div
                key={`grid-2-${idx}`}
                onClick={() => onImageClick && data && onImageClick(data, third + idx)}
                className="cursor-pointer hover:scale-105 transition-transform duration-300"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                <div className="overflow-hidden rounded-xl shadow-xl">
                  <img
                    src={el}
                    className="h-80 w-full object-cover object-left-top rounded-lg transition-transform duration-300 hover:scale-110"
                    alt="thumbnail"
                  />
                </div>
              </motion.div>
            );
          })}
        </div>
        <div className="grid gap-10">
          {thirdPart.map((el, idx) => {
            const data = getDataForIndex(idx, 'third');
            return (
              <motion.div
                style={{
                  y: translateYThird,
                  x: translateXThird,
                  rotateZ: rotateXThird,
                }}
                key={`grid-3-${idx}`}
                onClick={() => onImageClick && data && onImageClick(data, 2 * third + idx)}
                className="cursor-pointer hover:scale-105 transition-transform duration-300"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                <div className="overflow-hidden rounded-xl shadow-xl">
                  <img
                    src={el}
                    className="h-80 w-full object-cover object-left-top rounded-lg transition-transform duration-300 hover:scale-110"
                    alt="thumbnail"
                  />
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
