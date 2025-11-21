import { useScroll, useTransform, motion } from "framer-motion";
import { useRef } from "react";
import { cn } from "../../lib/utils";

interface Image {
  src: string;
  alt?: string;
}

interface ZoomParallaxProps {
  /** Array of images to be displayed in the parallax effect max 7 images */
  images: Image[];
  imageData?: any[];
  onImageClick?: (data: any, index: number) => void;
  className?: string;
}

export function ZoomParallax({ images, imageData = [], onImageClick, className }: ZoomParallaxProps) {
  const container = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: container,
    offset: ["start start", "end end"],
  });

  const scale3 = useTransform(scrollYProgress, [0, 1], [0.8, 3]);
  const scale4 = useTransform(scrollYProgress, [0, 1], [0.7, 4]);
  const scale5 = useTransform(scrollYProgress, [0, 1], [0.6, 5]);
  const scale6 = useTransform(scrollYProgress, [0, 1], [0.5, 6]);
  const scale8 = useTransform(scrollYProgress, [0, 1], [0.4, 8]);
  const scale9 = useTransform(scrollYProgress, [0, 1], [0.3, 9]);

  const scales = [scale3, scale4, scale5, scale4, scale5, scale6, scale8];

  return (
    <div ref={container} className={cn("relative h-[150vh]", className)}>
      <div className="sticky top-0 h-screen overflow-hidden">
        {images.map(({ src, alt }, index) => {
          const scale = scales[index % scales.length];

          return (
            <motion.div
              key={index}
              style={{ scale }}
              className={cn(
                "absolute top-0 flex h-full w-full items-center justify-center cursor-pointer hover:brightness-110 transition-all duration-300",
                index === 1 ? "[&>div]:!-top-[30vh] [&>div]:!left-[5vw] [&>div]:!h-[30vh] [&>div]:!w-[35vw]" : "",
                index === 2 ? "[&>div]:!-top-[10vh] [&>div]:!-left-[25vw] [&>div]:!h-[45vh] [&>div]:!w-[20vw]" : "",
                index === 3 ? "[&>div]:!left-[27.5vw] [&>div]:!h-[25vh] [&>div]:!w-[25vw]" : "",
                index === 4 ? "[&>div]:!top-[27.5vh] [&>div]:!left-[5vw] [&>div]:!h-[25vh] [&>div]:!w-[20vw]" : "",
                index === 5 ? "[&>div]:!top-[27.5vh] [&>div]:!-left-[22.5vw] [&>div]:!h-[25vh] [&>div]:!w-[30vw]" : "",
                index === 6 ? "[&>div]:!top-[22.5vh] [&>div]:!left-[25vw] [&>div]:!h-[15vh] [&>div]:!w-[15vw]" : ""
              )}
              onClick={() => onImageClick && onImageClick(imageData[index] || images[index], index)}
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <div className="relative h-[25vh] w-[25vw]">
                <img
                  src={src || "/placeholder.svg"}
                  alt={alt || `Parallax image ${index + 1}`}
                  className="h-full w-full object-cover rounded-xl shadow-2xl"
                />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
