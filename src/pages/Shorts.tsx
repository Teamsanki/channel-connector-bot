import { useState, useEffect } from "react";
import { collection, getDocs } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { Card } from "@/components/ui/card";
import Navigation from "@/components/Navigation";

const Shorts = () => {
  const [shorts, setShorts] = useState<any[]>([]);

  useEffect(() => {
    const fetchShorts = async () => {
      const querySnapshot = await getDocs(collection(db, "shorts"));
      const shortsData = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setShorts(shortsData);
    };
    fetchShorts();
  }, []);

  return (
    <div className="pb-20">
      <div className="p-4 space-y-4">
        {shorts.map((short) => (
          <Card key={short.id} className="aspect-[9/16] bg-gray-100">
            <video
              src={short.videoUrl}
              className="w-full h-full object-cover"
              controls
            />
          </Card>
        ))}
      </div>
      <Navigation />
    </div>
  );
};

export default Shorts;