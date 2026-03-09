package com.zawamil.app

import android.app.AlertDialog
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.ListView
import android.widget.SeekBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.net.URL

class MainActivity : AppCompatActivity() {

    // استبدل الرابط التالي برابط ملف data.json الخاص بك
    val dataUrl = "https://YOUR_USERNAME.github.io/zawamil-app/data.json"
    
    val mediaPlayer = MediaPlayer()
    val handler = Handler(Looper.getMainLooper())
    var audioList = mutableListOf<Map<String, String>>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // إعداد المشغل
        mediaPlayer.setAudioAttributes(
            AudioAttributes.Builder()
                .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                .setUsage(AudioAttributes.USAGE_MEDIA)
                .build()
        )

        // تحميل البيانات
        Thread {
            try {
                val jsonStr = URL(dataUrl).readText()
                val json = JSONObject(jsonStr)
                val years = json.keys()
                
                while(years.hasNext()) {
                    val year = years.next()
                    val arr = json.getJSONArray(year)
                    for (i in 0 until arr.length()) {
                        val item = arr.getJSONObject(i)
                        val map = mapOf(
                            "title" to "${item.getString("title")} ($year)",
                            "url" to item.getString("url")
                        )
                        audioList.add(map)
                    }
                }
                
                runOnUiThread {
                    setupList()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Toast.makeText(this, "فشل تحميل البيانات", Toast.LENGTH_LONG).show()
                }
            }
        }.start()
    }

    fun setupList() {
        val listView = findViewById<ListView>(R.id.listView)
        val titles = audioList.map { it["title"] ?: "" }
        val adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, titles)
        listView.adapter = adapter

        listView.onItemClickListener = AdapterView.OnItemClickListener { _, _, position, _ ->
            showPlayer(position)
        }
    }

    fun showPlayer(index: Int) {
        val audio = audioList[index]
        val url = audio["url"] ?: ""
        val title = audio["title"] ?: ""

        val dialogView = LayoutInflater.from(this).inflate(R.layout.player_dialog, null)
        val dialog = AlertDialog.Builder(this).setView(dialogView).create()

        val tvTitle = dialogView.findViewById<TextView>(R.id.tvTitle)
        val btnPlay = dialogView.findViewById<Button>(R.id.btnPlay)
        val btnStop = dialogView.findViewById<Button>(R.id.btnStop)
        val seekBar = dialogView.findViewById<SeekBar>(R.id.seekBar)

        tvTitle.text = title
        
        // تحديث شريط التقدم
        val updateRunnable = object : Runnable {
            override fun run() {
                if (mediaPlayer.isPlaying) {
                    seekBar.max = mediaPlayer.duration
                    seekBar.progress = mediaPlayer.currentPosition
                    handler.postDelayed(this, 1000)
                }
            }
        }

        btnPlay.setOnClickListener {
            if (!mediaPlayer.isPlaying) {
                mediaPlayer.reset()
                try {
                    mediaPlayer.setDataSource(url)
                    mediaPlayer.prepare()
                    mediaPlayer.start()
                    handler.post(updateRunnable)
                    btnPlay.text = "إيقاف مؤقت"
                } catch (e: Exception) {
                    Toast.makeText(this, "لا يمكن تشغيل هذا الملف", Toast.LENGTH_SHORT).show()
                }
            } else {
                mediaPlayer.pause()
                btnPlay.text = "تشغيل"
            }
        }

        btnStop.setOnClickListener {
            mediaPlayer.stop()
            handler.removeCallbacks(updateRunnable)
            dialog.dismiss()
        }

        dialog.setOnDismissListener {
            // mediaPlayer.stop() // اختياري: لإيقاف الصوت عند إغلاق النافذة
        }

        dialog.show()
    }
}
