# PulseOps System Architecture

## Overview
PulseOps is an asynchronous job processing system designed around decoupled microservices. The architecture segregates HTTP traffic processing from compute-heavy worker processing through an in-memory Redis message broker and persistent PostgreSQL store.

## Component Diagram

```text
  [ Client Browser ]
          │
          ▼
   [ Nginx Web Frontend ]
          │
          ▼
    [ FastAPI Service ] ─── (State Checks) ───► [ PostgreSQL DB ]
          │
          ▼ (Enqueue Job)
    [ Redis Job Queue ]
          ▲
          │ (Dequeue Job)
  [ Worker Processing Engine ]