import React, { useState } from 'react';

export default function LaserOverlay({
  matches = [],
  mockupNodes = {},
  domNodes = {},
  selectedNodeId = null,
  onSelectNode = () => {},
  showMockupBoxes = true,
  showDomBoxes = true,
  showLasers = true,
  showLabels = true,
}) {
  const [hoveredMatch, setHoveredMatch] = useState(null);

  return (
    <svg
      viewBox="0 0 1440 1000"
      className="absolute inset-0 w-full h-full pointer-events-auto"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        {/* Glow Filters */}
        <filter id="laserGlowCyan" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter id="laserGlowRose" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        {/* Marker Arrows */}
        <marker
          id="arrowCyan"
          viewBox="0 0 10 10"
          refX="6"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M 0 1 L 8 5 L 0 9 z" fill="#38BDF8" />
        </marker>
        <marker
          id="arrowRose"
          viewBox="0 0 10 10"
          refX="6"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M 0 1 L 8 5 L 0 9 z" fill="#F43F5E" />
        </marker>
      </defs>

      {matches.map((pair, idx) => {
        const mNode = mockupNodes[pair.mockup_node_id];
        const dNode = domNodes[pair.dom_node_id];

        if (!mNode || !dNode) return null;

        const mBox = mNode.bounding_box;
        const dBox = dNode.bounding_box;

        const mcx = mBox.x + mBox.width / 2;
        const mcy = mBox.y + mBox.height / 2;
        const dcx = dBox.x + dBox.width / 2;
        const dcy = dBox.y + dBox.height / 2;

        const isHovered =
          hoveredMatch?.mockup_node_id === pair.mockup_node_id ||
          selectedNodeId === pair.mockup_node_id;

        const hasDisplacement = pair.displacement.distance > 4.0;
        const hasColorDrift = pair.delta_e > 6.0;
        const isDefective = hasDisplacement || hasColorDrift || pair.ciou < 0.70;

        const laserColor = isDefective ? '#F43F5E' : '#38BDF8';
        const laserFilter = isDefective ? 'url(#laserGlowRose)' : 'url(#laserGlowCyan)';

        return (
          <g
            key={`match_${pair.mockup_node_id}_${idx}`}
            className="cursor-pointer transition-opacity duration-200"
            style={{ opacity: selectedNodeId && !isHovered ? 0.25 : 1.0 }}
            onMouseEnter={() => setHoveredMatch(pair)}
            onMouseLeave={() => setHoveredMatch(null)}
            onClick={() => onSelectNode(pair.mockup_node_id)}
          >
            {/* Expected Box (Mockup) - Cyan Dashed */}
            {showMockupBoxes && (
              <rect
                x={mBox.x}
                y={mBox.y}
                width={mBox.width}
                height={mBox.height}
                fill={isHovered ? 'rgba(56, 189, 248, 0.15)' : 'none'}
                stroke="#38BDF8"
                strokeWidth={isHovered ? 2.5 : 1.5}
                strokeDasharray="5 3"
                rx={4}
              />
            )}

            {/* Actual Box (DOM) - Rose/Emerald Solid */}
            {showDomBoxes && (
              <rect
                x={dBox.x}
                y={dBox.y}
                width={dBox.width}
                height={dBox.height}
                fill={isHovered ? (isDefective ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)') : 'none'}
                stroke={isDefective ? '#F43F5E' : '#10B981'}
                strokeWidth={isHovered ? 2.5 : 1.5}
                rx={4}
              />
            )}

            {/* Connecting Displacement Laser Vector */}
            {showLasers && hasDisplacement && (
              <>
                <line
                  x1={mcx}
                  y1={mcy}
                  x2={dcx}
                  y2={dcy}
                  stroke={laserColor}
                  strokeWidth={isHovered ? 3 : 2}
                  strokeDasharray="4 4"
                  filter={laserFilter}
                  markerEnd={isDefective ? 'url(#arrowRose)' : 'url(#arrowCyan)'}
                />
                {/* Center dot at mockup */}
                <circle cx={mcx} cy={mcy} r={isHovered ? 4 : 2.5} fill="#38BDF8" />
                {/* Center dot at DOM */}
                <circle cx={dcx} cy={dcy} r={isHovered ? 4 : 2.5} fill={laserColor} />
              </>
            )}

            {/* Metric Badge Pill */}
            {showLabels && (isHovered || (isDefective && pair.importance >= 2.0)) && (
              <g transform={`translate(${dcx + 8}, ${dcy - 12})`}>
                <rect
                  x={0}
                  y={0}
                  width={hasDisplacement ? 120 : 90}
                  height={22}
                  rx={4}
                  fill="#0B0F14"
                  stroke={laserColor}
                  strokeWidth={1}
                />
                <text
                  x={6}
                  y={15}
                  fill="#F8FAFC"
                  fontSize="10"
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  {hasDisplacement
                    ? `Δ: ${pair.displacement.distance}px`
                    : `CIoU: ${(pair.ciou * 100).toFixed(0)}%`}
                  {pair.delta_e > 4 && ` | ΔE:${pair.delta_e.toFixed(0)}`}
                </text>
              </g>
            )}
          </g>
        );
      })}

      {/* Floating Detailed Inspection Card when hovered */}
      {hoveredMatch && (
        <g transform="translate(24, 24)">
          <rect
            x={0}
            y={0}
            width={340}
            height={150}
            rx={8}
            fill="#111923"
            stroke="#38BDF8"
            strokeWidth={1.5}
            className="shadow-2xl"
          />
          <text x={16} y={28} fill="#38BDF8" fontSize="12" fontFamily="monospace" fontWeight="bold">
            FORENSIC NODE: {hoveredMatch.semantic_role.toUpperCase()}
          </text>
          <text x={16} y={50} fill="#94A3B8" fontSize="11" fontFamily="sans-serif">
            Displacement Vector:
          </text>
          <text x={160} y={50} fill="#FFFFFF" fontSize="11" fontFamily="monospace" fontWeight="bold">
            {hoveredMatch.displacement.distance}px (dx: {hoveredMatch.displacement.dx}px, dy: {hoveredMatch.displacement.dy}px)
          </text>
          <text x={16} y={72} fill="#94A3B8" fontSize="11" fontFamily="sans-serif">
            Complete IoU (CIoU):
          </text>
          <text x={160} y={72} fill="#FFFFFF" fontSize="11" fontFamily="monospace" fontWeight="bold">
            {hoveredMatch.ciou.toFixed(4)} (Cost: {hoveredMatch.c_geometry.toFixed(4)})
          </text>
          <text x={16} y={94} fill="#94A3B8" fontSize="11" fontFamily="sans-serif">
            Perceptual ΔE (CIE LAB):
          </text>
          <text x={160} y={94} fill="#FFFFFF" fontSize="11" fontFamily="monospace" fontWeight="bold">
            {hoveredMatch.delta_e.toFixed(1)} (Cost: {hoveredMatch.c_color.toFixed(4)})
          </text>
          <text x={16} y={116} fill="#94A3B8" fontSize="11" fontFamily="sans-serif">
            Text & SSIM Quality:
          </text>
          <text x={160} y={116} fill="#FFFFFF" fontSize="11" fontFamily="monospace" fontWeight="bold">
            Sim: {(hoveredMatch.text_sim * 100).toFixed(0)}% | SSIM: {hoveredMatch.raw_ssim.toFixed(2)}
          </text>
          <text x={16} y={138} fill="#10B981" fontSize="11" fontFamily="monospace" fontWeight="bold">
            Match Confidence: {(hoveredMatch.match_confidence * 100).toFixed(1)}% | Q_i: {hoveredMatch.quality_score.toFixed(3)}
          </text>
        </g>
      )}
    </svg>
  );
}

