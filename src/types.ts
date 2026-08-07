/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type QueryLevel = 'N0' | 'N1' | 'N2' | 'Panthéon Cognitif' | 'V8-OMEGA' | 'Cypher ODV' | 'Standard' | 'Phenix ODV' | 'RATISS V9 Aeon Prime';
export type CalculationMode = 
  | 'RATISS V9 Aeon Prime (Kernel Souverain)'
  | 'RATISS Cypher ODV'
  | 'V8-OMEGA (Topologique)'
  | 'Panthéon Cognitif (30 Moteurs)' 
  | 'Phenix ODV (Competition)'
  | 'Ontologique (N2)'
  | 'Standard (N1)';

export interface Message {
  id: string;
  role: 'user' | 'system' | 'assistant';
  content: string;
  timestamp: Date;
  level?: QueryLevel;
  imageUrl?: string;
  reasoning?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  level: QueryLevel;
  mode?: CalculationMode;
}

export interface SystemStatus {
  apiPortActive: boolean;
  isThinking: boolean;
  activeMoteur?: string;
}

export type InterfaceTheme = 'sovereign' | 'quantum' | 'minimalist';
