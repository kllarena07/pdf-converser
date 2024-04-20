"use client";

import { ConversationMessage } from "./type";

export default function Conversation({ conversation } : { conversation: ConversationMessage[] }) {
  return (
    <section className="h-[calc(100dvh-158px)] overflow-y-scroll">
      <ul>
        {conversation.map(({ query, result }, index) => (
          <li key={index}>
            <p>{query}</p>
            <p>{result}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}