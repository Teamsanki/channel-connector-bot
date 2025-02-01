import { useState, useEffect } from "react";
import { collection, getDocs } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Navigation from "@/components/Navigation";
import { Phone, Video } from "lucide-react";

const Calls = () => {
  const [calls, setCalls] = useState<any[]>([]);

  useEffect(() => {
    const fetchCalls = async () => {
      const querySnapshot = await getDocs(collection(db, "calls"));
      const callsData = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setCalls(callsData);
    };
    fetchCalls();
  }, []);

  return (
    <div className="pb-20">
      <div className="p-4 space-y-4">
        {calls.map((call) => (
          <Card key={call.id} className="cursor-pointer hover:bg-gray-50">
            <CardHeader className="flex flex-row justify-between items-center">
              <span className="font-bold">{call.username}</span>
              <div className="space-x-2">
                <Button variant="ghost" size="icon">
                  <Phone className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Video className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="text-gray-500">
              {call.lastCall}
            </CardContent>
          </Card>
        ))}
      </div>
      <Navigation />
    </div>
  );
};

export default Calls;