"use client";

type Conversation = {
  query: string;
  result: string;
}

export default function Conversation({ conversation } : { conversation: Conversation }) {
  return (
    <section className="h-[calc(100dvh-158px)] overflow-y-scroll">

    </section>
  )
}