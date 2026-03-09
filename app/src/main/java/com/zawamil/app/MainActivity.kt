package com.zawamil.app

import android.app.AlertDialog
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.ListView
import android.widget.SeekBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    // 1. إعداد المشغل والمتغيرات
    val mediaPlayer = MediaPlayer()
    val handler = Handler(Looper.getMainLooper())
    
    // 2. بيانات تجريبية (مضمونة للعمل)
    // تم وضع روابط صوتية تجريبية تعمل 100% لتجربة التطبيق
    val audioList = mutableListOf<Map<String, String>>(
        mapOf("title" to "زامل عيسى الليث 2024 - الأول", "url" to "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"),
        mapOf("title" to "زامل عيسى الليث 2024 - الثاني", "url" to "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"),
        mapOf("title" to "زامل عيسى الليث 2023 - الثالث", "url" to "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"),
        mapOf("title" to "زامل عيسى الليث 2022 - الرابع", "url" to "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3")
    )
    
    var currentAudioIndex = -1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // 3. إعداد خصائص الصوت
        mediaPlayer.setAudioAttributes(
            AudioAttributes.Builder()
                .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                .setUsage(AudioAttributes.USAGE_MEDIA)
                .build()
        )

        // 4. عرض القائمة فوراً
        setupList()
    }

    fun setupList() {
        val listView = findViewById<ListView>(R.id.listView)
        // استخراج العناوين فقط للعرض
        val titles = audioList.map { it["title"] ?: "زامل غير معروف" }
        
        // استخدام ArrayAdapter بسيط
        val adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, titles)
        listView.adapter = adapter

        // عند النقر على عنصر
        listView.onItemClickListener = AdapterView.OnItemClickListener { _, _, position, _ ->
            showPlayer(position)
        }
    }

    fun showPlayer(index: Int) {
        val audio = audioList[index]
        val url = audio["url"] ?: ""
        val title = audio["title"] ?: ""

        // تجهيز نافذة المشغل
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

        // زر التشغيل والإيقاف
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

        // زر الإيقاف والإغلاق
        btnStop.setOnClickListener {
            mediaPlayer.stop()
            handler.removeCallbacks(updateRunnable)
            dialog.dismiss()
        }
        
        // عند إغلاق النافذة
        dialog.setOnDismissListener {
            handler.removeCallbacks(updateRunnable)
        }

        dialog.show()
    }
}
