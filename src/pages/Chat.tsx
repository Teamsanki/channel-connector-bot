import { useState, useEffect } from "react";
import { collection, getDocs } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import Navigation from "@/components/Navigation";

const Chat = () => {
  const [chats, setChats] = useState<any[]>([]);

  useEffect(() => {
    const fetchChats = async () => {
      const querySnapshot = await getDocs(collection(db, "chats"));
      const chatsData = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setChats(chatsData);
    };
    fetchChats();
  }, []);

  return (
    <div className="pb-20">
      <div className="p-4 space-y-4">
        {chats.map((chat) => (
          <Card key={chat.id} className="cursor-pointer hover:bg-gray-50">
            <CardHeader className="font-bold">{chat.username}</CardHeader>
            <CardContent className="text-gray-500">
              {chat.lastMessage}
            </CardContent>
          </Card>
        ))}
      </div>
      <Navigation />
    </div>
  );
};

export default Chat;