import { Input } from "@/components/ui/input"
import Conversation from "./_conversation/conversation";
import { useState } from "react";
import { ConversationMessage } from "./_conversation/type";

export default function Home() {
  const [conversation, setConversation] = useState([] as ConversationMessage[])

  const uploadFile = async (formData: FormData) => {
    "use server";

    const response = await fetch("http://127.0.0.1:8000/extract/", {
      method: "POST",
      body: formData
    });
    console.log(await response.json());
  }

  const queryFile = async (formData: FormData) => {
    "use server";

    const response = await fetch("http://127.0.0.1:8000/query/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: formData.get("query"),
        filename: "lab7"
      })
    });
    console.log(await response.json());
  }

  return (
    <main className="flex flex-col">
      <header className="p-5">
        <form action={uploadFile}>
          <label>
            <Input name="pdf" type="file" accept="application/pdf" />
          </label>
        </form>
      </header>
      <Conversation conversation={[{ query: "Hello", result: "Hi" }]} />
      <footer className="w-full flex justify-center">
        <form action={queryFile} className="pb-5 w-4/5 relative">
          <label>
            <Input className="p-7" name="query" type="text" placeholder="Message uploaded PDF" />
          </label>
          <button disabled className="absolute disabled:cursor-not-allowed bottom-1.5 right-2 rounded-lg border border-black bg-black p-0.5 text-white transition-colors enabled:bg-black disabled:text-gray-400 disabled:opacity-10 dark:border-white dark:bg-white dark:hover:bg-white md:bottom-3 md:right-3" data-testid="send-button"><span class="" data-state="closed"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" class="text-white dark:text-black"><path d="M7 11L12 6L17 11M12 18V7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg></span></button>
        </form>
      </footer>
    </main>
  );
}
